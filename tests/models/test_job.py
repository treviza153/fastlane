from uuid import uuid4

from mongoengine.errors import ValidationError
from preggy import expect

from easyq.models.job import Job
from easyq.models.task import Task


def test_job_create(client):
    """Test creating a new job"""

    task_id = str(uuid4())

    t = Task.create_task(task_id, image='image', command='command')
    j = t.create_job()

    expect(j.job_id).to_equal(str(j.id))
    expect(j.created_at).not_to_be_null()
    expect(j.last_modified_at).not_to_be_null()
    expect(j.image).to_equal('image')
    expect(j.command).to_equal('command')

    expect(j.container_id).to_be_null()
    expect(j.status).to_equal(Job.Status.enqueued)


def test_job_get_by_job_id(client):
    """Test getting a job by id"""

    task_id = str(uuid4())
    t = Task.create_task(task_id, image='image', command='command')

    j = t.create_job()

    topic = Job.get_by_id(task_id, j.job_id)
    expect(topic).not_to_be_null()
    expect(topic.job_id).to_equal(str(j.id))

    topic = Job.get_by_id('invalid', 'invalid')
    expect(topic).to_be_null()
