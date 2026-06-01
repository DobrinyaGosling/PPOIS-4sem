import argparse
from functools import partial


class CliArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, out, err, **kwargs):
        super().__init__(*args, **kwargs)
        self._out = out
        self._err = err

    def _print_message(self, message, file=None):
        if not message:
            return
        target = self._err if file is None else file
        try:
            target.write(message)
        except Exception:
            self._err.write(message)


def build_parser(out, err) -> argparse.ArgumentParser:
    parser = CliArgumentParser(
        prog="vdept",
        description="Virtual Department CLI",
        out=out,
        err=err,
    )
    sub = parser.add_subparsers(
        dest="cmd",
        required=True,
        parser_class=partial(CliArgumentParser, out=out, err=err),
    )

    p = sub.add_parser("create-student", help="Create a student")
    p.add_argument("--login", required=True)
    p.add_argument("--name", required=True)

    p = sub.add_parser("create-teacher", help="Create a teacher")
    p.add_argument("--login", required=True)
    p.add_argument("--name", required=True)

    sub.add_parser("list-students", help="List students")
    sub.add_parser("list-teachers", help="List teachers")

    p = sub.add_parser("add-material", help="Add study material")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)

    sub.add_parser("list-materials", help="List materials")

    p = sub.add_parser("add-assignment", help="Add assignment")
    p.add_argument("--title", required=True)
    p.add_argument("--description", required=True)

    sub.add_parser("list-assignments", help="List assignments")
    sub.add_parser("list-submissions", help="List submissions")

    p = sub.add_parser("submit-assignment", help="Submit assignment answer")
    p.add_argument("--assignment-id", required=True)
    p.add_argument("--student-id", required=True)
    p.add_argument("--answer", required=True)

    p = sub.add_parser("grade-submission", help="Grade a submission")
    p.add_argument("--submission-id", required=True)
    p.add_argument("--grade", required=True, type=int)

    p = sub.add_parser("create-test", help="Create a test from JSON")
    p.add_argument("--title", required=True)
    p.add_argument(
        "--questions-json",
        required=True,
        help="JSON array: [{prompt, options:[...], correct_index:int}, ...]",
    )

    p = sub.add_parser("take-test", help="Take a test (answers JSON)")
    p.add_argument("--test-id", required=True)
    p.add_argument("--student-id", required=True)
    p.add_argument("--answers-json", required=True, help="JSON array of option indices")

    sub.add_parser("list-tests", help="List tests")
    sub.add_parser("list-attempts", help="List test attempts")

    p = sub.add_parser("create-thread", help="Create forum thread")
    p.add_argument("--title", required=True)

    p = sub.add_parser("post", help="Add post to a thread")
    p.add_argument("--thread-id", required=True)
    p.add_argument("--author-id", required=True)
    p.add_argument("--content", required=True)

    sub.add_parser("list-threads", help="List forum threads")

    p = sub.add_parser("schedule-lecture", help="Schedule a lecture")
    p.add_argument("--topic", required=True)

    p = sub.add_parser("start-lecture", help="Start a scheduled lecture")
    p.add_argument("--lecture-id", required=True)

    p = sub.add_parser("end-lecture", help="End a live lecture")
    p.add_argument("--lecture-id", required=True)

    sub.add_parser("list-lectures", help="List lectures")

    return parser
