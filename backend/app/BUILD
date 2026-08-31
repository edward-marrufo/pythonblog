load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "app",
    srcs = glob(["**/*.py"]),
    deps = [
        "@pypi//fastapi:pkg",
        "@pypi//passlib:pkg",
        "@pypi//user_agents:pkg",
        "@pypi//httpx:pkg",
    ],
    visibility = ["//backend/tests:__pkg__"],
)