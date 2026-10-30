from datetime import datetime, timedelta, timezone
from hashlib import sha256
from unittest.mock import Mock

import pytest

from application_automation.approvals import Approval, content_digest, require_approval
from application_automation.forms import Field, prepare_socket_pilot, submit_application
from application_automation.models import Applicant, Job
from application_automation.resumes import ResumeVariant
from application_automation.scoring import Criterion, qualify
from application_automation.tracking import Tracker


@pytest.mark.parametrize('match,eligible', [(0.79, False), (0.80, True), (1, True)])
def test_qualification_boundary(match, eligible):
    assert qualify([Criterion('skills', 1, match, 'verified')]).eligible is eligible


def test_missing_evidence_blocks_even_high_score():
    result = qualify([Criterion('skills', 1, 1, '')])
    assert result.score == 100
    assert not result.eligible
    assert result.missing_evidence == ('skills',)
    assert not qualify([Criterion('skills', 1, None, 'unknown')]).eligible


@pytest.mark.parametrize('weight,match', [(0, 1), (float('nan'), 1), (1, 2)])
def test_invalid_scoring(weight, match):
    with pytest.raises(ValueError):
        qualify([Criterion('skills', weight, match, 'verified')])


def test_approval_is_exact_and_expires():
    payload = {'url': 'https://example.com'}
    approval = Approval('prepare_form', content_digest(payload), 'Reviewer', datetime.now(timezone.utc) + timedelta(hours=1))
    require_approval(approval, 'prepare_form', payload)
    with pytest.raises(PermissionError):
        require_approval(approval, 'prepare_form', {'url': 'https://other.example'})
    with pytest.raises(PermissionError):
        require_approval(Approval('prepare_form', content_digest(payload), 'Reviewer', datetime.now(timezone.utc) - timedelta(seconds=1)), 'prepare_form', payload)


def test_resume_change_invalidates_approval(tmp_path):
    path = tmp_path / 'resume.pdf'
    path.write_bytes(b'fixture')
    variant = ResumeVariant('test', path, sha256(path.read_bytes()).hexdigest())
    assert variant.verify() == path
    path.write_bytes(b'changed')
    with pytest.raises(ValueError):
        variant.verify()


def test_tracking_persists_and_rejects_submission(tmp_path):
    path = tmp_path / 'data' / 'events.db'
    Tracker(path).record('job-1', 'awaiting_final_review')
    assert Tracker(path).events() == [('job-1', 'awaiting_final_review')]
    with pytest.raises(ValueError):
        Tracker(path).record('job-1', 'submitted')


@pytest.fixture
def pilot(tmp_path):
    path = tmp_path / 'resume.pdf'
    path.write_bytes(b'test-only resume fixture')
    digest = sha256(path.read_bytes()).hexdigest()
    url = 'https://jobs.ashbyhq.com/socket/test-role'
    payload = {'url': url, 'fields': {'Full name': 'Test Applicant'}, 'resume_sha256': digest,
               'resume_label': 'Resume', 'site_review': 'Test-only site review'}
    return dict(page=Mock(url=url), job=Job('test', 'Socket', 'Test role', url),
                applicant=Applicant({'name': 'Test Applicant'}),
                qualification=qualify([Criterion('skills', 1, 1, 'test evidence')]),
                fields=[Field('Full name', 'name')], resume=ResumeVariant('test', path, digest),
                resume_label='Resume', site_review=payload['site_review'],
                approval=Approval('prepare_form', content_digest(payload), 'Test reviewer', datetime.now(timezone.utc) + timedelta(hours=1)))


def test_preparation_stops_before_submission(pilot):
    assert prepare_socket_pilot(**pilot) == 'awaiting_final_review'
    page = pilot['page']
    page.get_by_label.assert_any_call('Full name', exact=True)
    page.get_by_label.return_value.fill.assert_called_once_with('Test Applicant')
    page.get_by_label.return_value.set_input_files.assert_called_once()
    assert not page.get_by_label.return_value.click.called
    with pytest.raises(PermissionError):
        submit_application()


@pytest.mark.parametrize('problem', ['missing_fact', 'low_score', 'no_review', 'wrong_approval', 'wrong_host', 'changed_resume'])
def test_block_before_browser_access(pilot, problem):
    if problem == 'missing_fact':
        pilot['applicant'] = Applicant({})
    elif problem == 'low_score':
        pilot['qualification'] = qualify([Criterion('skills', 1, .79, 'test evidence')])
    elif problem == 'no_review':
        pilot['site_review'] = ''
    elif problem == 'wrong_approval':
        pilot['approval'] = Approval('prepare_form', 'wrong', 'Test', datetime.now(timezone.utc) + timedelta(hours=1))
    elif problem == 'wrong_host':
        pilot['job'] = Job('test', 'Socket', 'Test', 'https://evil.example/socket/test')
    else:
        pilot['resume'].path.write_bytes(b'changed')
    with pytest.raises((PermissionError, ValueError)):
        prepare_socket_pilot(**pilot)
    pilot['page'].goto.assert_not_called()


def test_redirect_stops_before_personal_data(pilot):
    pilot['page'].url = 'https://other.example/'
    with pytest.raises(PermissionError):
        prepare_socket_pilot(**pilot)
    pilot['page'].get_by_label.assert_not_called()


def test_curated_discovery_validates_destination(tmp_path):
    import json
    from application_automation.discovery import load_jobs
    path = tmp_path / 'jobs.json'
    row = dict(id='test', company='Socket', title='Test', url='https://jobs.ashbyhq.com/socket/test')
    path.write_text(json.dumps([row]))
    assert load_jobs(path)[0].company == 'Socket'
    row['url'] = 'https://user:password@example.com/job'
    path.write_text(json.dumps([row]))
    with pytest.raises(ValueError):
        load_jobs(path)
