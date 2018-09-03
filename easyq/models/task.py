import datetime

import mongoengine.errors
from bson.objectid import ObjectId
from mongoengine import (BooleanField, DateTimeField, ListField,
                         ReferenceField, StringField)

from easyq.models import db


class Task(db.Document):
    created_at = DateTimeField(required=True)
    last_modified_at = DateTimeField(
        required=True, default=datetime.datetime.now)
    task_id = StringField(required=True)
    done = BooleanField(required=True, default=False)
    jobs = ListField(ReferenceField('Job'))
    pattern = StringField(required=False)
    image = StringField(required=True)
    command = StringField(required=True)

    def _validate(self):
        errors = {}

        if self.task_id == "":
            errors["task_id"] = mongoengine.errors.ValidationError(
                'Field is required', field_name="task_id")

        if self.image == "":
            errors["image"] = mongoengine.errors.ValidationError(
                'Field is required', field_name="image")

        if self.command == "":
            errors["command"] = mongoengine.errors.ValidationError(
                'Field is required', field_name="command")

        if errors:
            message = 'ValidationError (%s:%s) ' % (self._class_name, self.pk)
            raise mongoengine.errors.ValidationError(message, errors=errors)

    def save(self, *args, **kwargs):
        self._validate()

        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.last_modified_at = datetime.datetime.now()

        return super(Task, self).save(*args, **kwargs)

    @classmethod
    def create_task(cls, task_id, image, command):
        t = cls(task_id=task_id, image=image, command=command, done=False)
        t.save()

        return t

    @classmethod
    def get_by_task_id(cls, task_id):
        if task_id is None or task_id == "":
            raise RuntimeError(
                "Task ID is required and can't be None or empty.")

        t = cls.objects(task_id=task_id).no_dereference().first()

        return t

    def create_job(self):
        from easyq.models.job import Job

        job_id = ObjectId()
        j = Job(
            id=job_id,
            job_id=str(job_id),
            status=Job.Status.enqueued,
            image=self.image,
            command=self.command,
        )
        j.task = self
        j.save()

        self.jobs.append(j)
        self.save()

        return j
