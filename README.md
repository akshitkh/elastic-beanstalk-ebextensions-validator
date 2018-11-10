<h1> AWS Elastic Beanstalk </h1>

**EBExtensions Option Settings Validator** 

########################### Akhit Khanna #########################
########################## AWS 2016 ##############################


Usage:

python ebXparser.py ebx_config_file


Release Notes:

-- Validates the formatting and option settings of ebextensions general option_settings

"http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-options-general.html"

-- Works with both the general and shorthand formats. eg:

General::

option_settings:
  - namespace: aws:autoscaling:asg
    option_name: Cooldown
    value: 500


Shorthand::

option_settings:
  aws:autoscaling:asg:
    Cooldown: 500


-- Sub Directory "configs" contains all the files for different namespaces that contain the option settings and allowed values that serve as reference.

-- aws:elb:policies:policy_name has not been implemented yet.

-- Options like "InstanceType" might be considered valid if they are entered as any string. Will update this later to allow only valid values.

-- Files under the "config" directory can be modified to add/delete/update option settings. 

-- YAML lint does not work very well with the shorthand version. 
