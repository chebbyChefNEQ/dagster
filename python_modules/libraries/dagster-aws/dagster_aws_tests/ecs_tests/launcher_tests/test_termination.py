def test_termination(instance, workspace, run):
    assert not instance.run_launcher.can_terminate(run.run_id)

    instance.launch_run(run.run_id, workspace)

    assert instance.run_launcher.can_terminate(run.run_id)
    assert instance.run_launcher.terminate(run.run_id)
    assert not instance.run_launcher.can_terminate(run.run_id)
    assert not instance.run_launcher.terminate(run.run_id)


def test_eventual_consistency(instance, workspace, run, monkeypatch):
    instance.launch_run(run.run_id, workspace)

    def empty(*_args, **_kwargs):
        return {"tasks": []}

    original = instance.run_launcher.ecs.describe_tasks

    # The ECS API is eventually consistent:
    # https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RunTask.html
    # describe_tasks might initially return nothing even if a task exists.
    monkeypatch.setattr(instance.run_launcher.ecs, "describe_tasks", empty)
    assert not instance.run_launcher.can_terminate(run.run_id)

    monkeypatch.setattr(instance.run_launcher.ecs, "describe_tasks", original)
    assert instance.run_launcher.can_terminate(run.run_id)

    monkeypatch.setattr(instance.run_launcher.ecs, "describe_tasks", empty)
    assert not instance.run_launcher.terminate(run.run_id)

    monkeypatch.setattr(instance.run_launcher.ecs, "describe_tasks", original)
    assert instance.run_launcher.terminate(run.run_id)
