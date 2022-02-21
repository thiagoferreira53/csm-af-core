from http import HTTPStatus

from flask import make_response
from pydantic import BaseModel


def json_response(response_model: BaseModel, http_status: HTTPStatus):

    response = make_response(response_model.json(exclude_none=True), http_status)
    response.mimetype = "application/json"

    return response
