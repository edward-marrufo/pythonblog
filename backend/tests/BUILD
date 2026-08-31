load("@rules_python//python:defs.bzl", "py_binary", "py_test")

py_binary(
    name = "pytest_runner",
    srcs = ["pytest_runner.py"],
    deps = [
        "@pypi//pytest",
    ],
)

py_test(
    name = "all",
    srcs = glob(["test_*.py"]) + ["pytest_runner.py"],
    main = "pytest_runner.py",
    deps = [
        "@pypi//pytest",
        "//backend/app:app",
        "//backend/tests/fakes:fakes",
    ],
)