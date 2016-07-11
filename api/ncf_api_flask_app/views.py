from ncf_api_flask_app import app
from flask import Flask, jsonify, request, abort
from functools import wraps
import requests
import os
import sys
import traceback
from pprint import pprint

# Add NCF_TOOLS_DIR to sys.path so we can access ncf module
NCF_TOOLS_DIR = '/usr/share/ncf/tools'
sys.path[0:0] = [NCF_TOOLS_DIR]

default_path = ""
use_rudder_auth = True

import ncf
import ncf_constraints

def format_error(exception, when, code):
  if not isinstance(exception, ncf.NcfError):
    exception = ncf.NcfError("Unknown internal error during " + when, "Cause: " + str(exception) + "\n" + traceback.format_exc())
  error = jsonify ({ "error": ncf.format_errors([exception]) })
  error.status_code = code
  return  error


def check_auth(f):
  """Method to use before each API call to check authentication"""
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = get_auth()
    if auth.status_code == 401:
      return auth
    return f(*args, **kwargs)
  return decorated


def check_authentication_from_rudder(auth_request):
  """Send an authentication request to Rudder"""
  if request.method == "GET":
    acl = "read"
  else:
    acl = "write"
  # An error may occured here and we need to catch the exception here or it will not be catched
  try:
    # We skip ssl certificate verification, since rudder and ncf-api are on the same domain and same virtualhost
    auth_result = requests.get('https://localhost/rudder/authentication?acl=' + acl, cookies =  request.cookies, verify = False)

    auth_response = jsonify( auth_result.json() )
    auth_response.status_code = auth_result.status_code

    return auth_response
  except Exception as e:
    error = jsonify ({ "error" : [{"message": "An error while authenticating to Rudder"}]})
    error.status_code = 500

    return error


def no_authentication(auth_request):
  """Always accept authentication request"""
  auth_response = auth_response = jsonify( {} )
  auth_response.status_code = 200

  return auth_response


def get_authentication_modules():
  """Find all available authentication modules"""
  # List of all authentication modules
  authentication_modules = { "Rudder" : check_authentication_from_rudder, "None" : no_authentication }
  # Name of all available modules, should read from a file or ncf path. only Rudder available for now
  available_modules_name = ["None"]
  if use_rudder_auth:
    available_modules_name = ["Rudder"]

  available_modules = [ module for module_name, module in authentication_modules.items() if module_name in available_modules_name ]
  return available_modules


@app.route('/api/auth', methods = ['GET'])
def get_auth():
  """ Check authentication, should look for available modules and pass authentication on them"""
  try:
    for authentication_module in get_authentication_modules():
      authentication_result = authentication_module(request)
      if authentication_result.status_code == 200:
        # Authentication success return it
        return authentication_result
    # all authentication have failed, return an error
    error = jsonify ({ "error" : [{"message": "Could not authenticate with ncf API"}]})
    error.status_code = 401
    return error
  except Exception as e:
    return format_error(e, "authentication", 500)


def get_path_from_args (request):
  """ Extract path argument from a request, if empty or missing use default one"""
  if "path" in request.args and request.args['path'] != "":
    return request.args['path']
  else:
    return default_path


@app.route('/api/techniques', methods = ['GET'])
@check_auth
def get_techniques():
  """Get all techniques from ncf folder passed as parameter, or default ncf folder if not defined"""
  try:
    # We need to get path from url params, if not present put "" as default value
    path = get_path_from_args(request)
    techniques = ncf.get_all_techniques_metadata(alt_path = path)
    resp = jsonify( techniques )
    return resp
  except Exception as e:
    return format_error(e, "techniques fetching", 500)



@app.route('/api/generic_methods', methods = ['GET'])
@check_auth
def get_generic_methods():
  """Get all generic methods from ncf folder passed as parameter, or default ncf folder if not defined"""
  try:
    # We need to get path from url params, if not present put "" as default value
    path = get_path_from_args(request)
  
    generic_methods = ncf.get_all_generic_methods_metadata(alt_path = path)
    generic_methods["data"]["usingRudder"] = use_rudder_auth
    resp = jsonify( generic_methods )
    return resp
  except Exception as e:
    return format_error(e, "generic methods fetching", 500)


@app.route('/api/techniques', methods = ['POST', "PUT"])
@check_auth
def create_technique():
  """ Get data in JSON """
  try:
    # technique is a mandatory parameter, abort if not present
    if not "technique" in request.json:
      return format_error(ncf.NcfError("No Technique metadata provided in the request body."), "", 400)
    else:
      technique = request.json['technique']
  
    if "path" in request.json and request.json['path'] != "":
      path = request.json['path']
    else:
      path = default_path
  
    ncf.write_technique(technique,path)
    return jsonify({ "data": technique }), 201

  except Exception as e:
    return format_error(e, "technique writing", 500)


@app.route('/api/techniques/<string:bundle_name>', methods = ['DELETE'])
@check_auth
def delete_technique(bundle_name):
  try:
    path = get_path_from_args(request)
    ncf.delete_technique(bundle_name,path)
    return jsonify({ "data": { "bundle_name" : bundle_name } })
  except Exception as e:
    return format_error(e, "technique deletion", 500)

@app.route('/api/check/parameter', methods = ['POST'])
@check_auth
def check_parameter():
  """Get all techniques from ncf folder passed as parameter, or default ncf folder if not defined"""
  try:
    if not "value" in request.json:
      return format_error(ncf.NcfError("No value metadata provided in the request body."), "", 400)
    else:
       parameter_value = request.json['value']

    if not "constraints" in request.json:
      return format_error(ncf.NcfError("No constraints metadata provided in the request body."), "", 400)
    else:
      parameter_constraints = request.json['constraints']
 
    # We need to get path from url params, if not present put "" as default value
    check = ncf_constraints.check_parameter(parameter_value,parameter_constraints)
    resp = jsonify( check )
    return resp
  except Exception as e:
    return format_error(e, "checking parameter", 500)



if __name__ == '__main__':
  app.run(debug = True)
