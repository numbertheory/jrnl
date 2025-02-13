# Copyright (C) 2012-2021 jrnl contributors
# License: https://www.gnu.org/licenses/gpl-3.0.html

import logging
import sys
import traceback

from .jrnl import run
from .args import parse_args
from jrnl.output import print_msg

from jrnl.exception import JrnlException
from jrnl.messages import Message
from jrnl.messages import MsgText
from jrnl.messages import MsgType


def configure_logger(debug=False):
    if not debug:
        logging.disable()
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(name)-12s %(message)s",
    )
    logging.getLogger("parsedatetime").setLevel(logging.INFO)
    logging.getLogger("keyring.backend").setLevel(logging.ERROR)


def cli(manual_args=None):
    try:
        if manual_args is None:
            manual_args = sys.argv[1:]

        args = parse_args(manual_args)
        configure_logger(args.debug)
        logging.debug("Parsed args: %s", args)

        status_code = run(args)

    except JrnlException as e:
        status_code = 1
        e.print()

    except KeyboardInterrupt:
        status_code = 1
        print_msg("\nKeyboardInterrupt", "\nAborted by user", msg=Message.ERROR)

    except Exception as e:
        # uncaught exception
        status_code = 1
        debug = False
        try:
            if args.debug:  # type: ignore
                debug = True
        except NameError:
            # This should only happen when the exception
            # happened before the args were parsed
            if "--debug" in sys.argv:
                debug = True

        if debug:
            print("\n")
            traceback.print_tb(sys.exc_info()[2])

        print_msg(
            Message(
                MsgText.UncaughtException,
                MsgType.ERROR,
                {"name": type(e).__name__, "exception": e},
            )
        )

    # This should be the only exit point
    return status_code
