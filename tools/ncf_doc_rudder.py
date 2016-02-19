#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: ./ncf_docrudder.py
#
# This is a Python module to generate documentation from generic methods in ncf to be embedded in Rudder manual

import ncf 

from pprint import pprint

def rudder_version(version):
  # CFEngine <=> Rudder versions

  # some generic methods have ">= version", others ">=version"
  canonified_version = version.replace(" ", "")
  
  cfengine_version = {}
  cfengine_version[">=3.5"] = "2.10"
  cfengine_version[">=3.6"] = "2.11"
  cfengine_version[">=3.7"] = "3.2"
    
  if canonified_version in cfengine_version:
    return cfengine_version[canonified_version]
  else:
    return "unknown"

if __name__ == '__main__':

  # Get all generic methods
  generic_methods = ncf.get_all_generic_methods_metadata()["data"]
  
  categories = {}
  for method_name in sorted(generic_methods.keys()):
    category_name = method_name.split('_',1)[0]
    generic_method = generic_methods[method_name]
    if (category_name in categories):
      categories[category_name].append(generic_method)
    else:
      categories[category_name] = [generic_method]

  content = []

  for category in sorted(categories.keys()):
    content.append('\n### '+category.title())
 
    # Generate markdown for each generic method
    for generic_method in categories[category]:
      bundle_name = generic_method["bundle_name"]
      content.append('\n#### '+ bundle_name)
      content.append(generic_method["description"])
      content.append('\nCompatible with nodes running Rudder '+rudder_version(generic_method["agent_version"])+' or higher.')
      
      if "documentation" in generic_method:
        content.append('\n##### Usage')
        content.append(generic_method["documentation"])
      content.append('\n##### Parameters')
      for parameter in generic_method["parameter"]:
        content.append("* **" + parameter['name'] + "**: " + parameter['description'])
      content.append('\n##### Classes defined')
      content.append('\n```\n')
      content.append(generic_method["class_prefix"]+"_${"+generic_method["class_parameter"] + "}_{kept, repaired, not_ok, reached}")
      content.append('\n```\n')

  # Write generic_methods.md
  result = '\n'.join(content)+"\n"
  outfile = open("doc/generic_methods_rudder.md","w")
  outfile.write(result)
  outfile.close()
