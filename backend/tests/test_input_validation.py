import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO
from modules.M01_input_sources.input_validation import validate_file_metadata, resolve_jd_input

@pytest.mark.parametrize(('filename','expected'), [('resume.pdf','.pdf'),('resume.DOCX','.docx')])
def test_allowed_extensions(filename, expected):
    assert validate_file_metadata(filename, b'content') == expected

def test_reject_unsupported_extension():
    with pytest.raises(HTTPException) as exc:
        validate_file_metadata('resume.txt', b'content')
    assert exc.value.status_code == 400

def test_reject_empty_file():
    with pytest.raises(HTTPException) as exc:
        validate_file_metadata('resume.pdf', b'')
    assert exc.value.status_code == 400

def test_reject_file_over_limit():
    with pytest.raises(HTTPException) as exc:
        validate_file_metadata('resume.pdf', b'x' * (5*1024*1024+1))
    assert exc.value.status_code == 413

def test_jd_text_only():
    assert resolve_jd_input(' Python developer ', None) == 'text'

def test_jd_file_only():
    file = UploadFile(filename='job.pdf', file=BytesIO(b'content'))
    assert resolve_jd_input(None, file) == 'file'

def test_jd_requires_exactly_one_input():
    with pytest.raises(HTTPException): resolve_jd_input(None, None)
    with pytest.raises(HTTPException): resolve_jd_input('JD', UploadFile(filename='job.pdf', file=BytesIO(b'x')))
