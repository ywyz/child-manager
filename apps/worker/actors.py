import dramatiq


@dramatiq.actor
def process_generation_job(job_id: str) -> None:
    pass


@dramatiq.actor
def process_export_job(job_id: str) -> None:
    pass


@dramatiq.actor
def process_retry_job(job_id: str) -> None:
    pass
