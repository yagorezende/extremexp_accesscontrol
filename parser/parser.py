import xml.etree.ElementTree as ET
import json
import re
import os

def strip_namespace(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]
    else:
        return tag

def parse_attribute_designator(element):
    return {
        'AttributeId': element.get('AttributeId'),
        'Category': element.get('Category'),
        'DataType': element.get('DataType'),
        'MustBePresent': element.get('MustBePresent')
    }

def parse_attribute_value(element):
    return {
        'DataType': element.get('DataType'),
        'Value': element.text.strip() if element.text else ''
    }

def parse_apply(element):
    apply_dict = {
        'FunctionId': element.get('FunctionId'),
        'Arguments': []
    }
    for child in element:
        tag = strip_namespace(child.tag)
        if tag == 'Apply':
            apply_dict['Arguments'].append(parse_apply(child))
        elif tag == 'AttributeDesignator':
            apply_dict['Arguments'].append({'AttributeDesignator': parse_attribute_designator(child)})
        elif tag == 'AttributeValue':
            apply_dict['Arguments'].append({'AttributeValue': parse_attribute_value(child)})
    return apply_dict

def parse_condition(element):
    condition = {}
    for child in element:
        tag = strip_namespace(child.tag)
        if tag == 'Apply':
            condition['Apply'] = parse_apply(child)
    return condition

def parse_obligations(element):
    obligations = []
    for obligation in element.findall('./*'):
        obligation_dict = {
            'ObligationId': obligation.get('ObligationId'),
            'FulfillOn': obligation.get('FulfillOn'),
            'AttributeAssignmentExpressions': []
        }
        for assignment in obligation.findall('./AttributeAssignmentExpression'):
            attribute_id = assignment.get('AttributeId')
            value_element = assignment.find('./{*}AttributeValue')
            if value_element is not None:
                attribute_value = parse_attribute_value(value_element)
                obligation_dict['AttributeAssignmentExpressions'].append({
                    'AttributeId': attribute_id,
                    'Value': attribute_value
                })
        obligations.append(obligation_dict)
    return obligations

def parse_description(description_text):
    description_dict = {}
    pattern = r'([\w\s]+):\s+(.+?)(?=\n[\w\s]+:|$)'
    matches = re.findall(pattern, description_text, re.DOTALL)
    for key, value in matches:
        description_dict[key.strip()] = value.strip()
    return description_dict if description_dict else description_text.strip()

def process_rule(rule):
    rule_dict = {
        'RuleId': rule.get('RuleId'),
        'Effect': rule.get('Effect'),
        'Description': None,
        'Target': None,
        'Condition': None,
        'Obligations': None
    }

    description = rule.find('./{*}Description')
    if description is not None:
        description_text = description.text.strip()
        rule_dict['Description'] = parse_description(description_text)

    target = rule.find('./{*}Target')
    condition = rule.find('./{*}Condition')
    if condition is not None:
        rule_dict['Condition'] = parse_condition(condition)

    obligations_element = rule.find('./{*}ObligationExpressions')
    if obligations_element is not None:
        rule_dict['Obligations'] = parse_obligations(obligations_element)

    return rule_dict

def process_policy(root):
    policy_dict = {
        'PolicyId': root.get('PolicyId'),
        'RuleCombiningAlgId': root.get('RuleCombiningAlgId'),
        'Version': root.get('Version'),
        'Description': None,
        'Target': None,
        'Rules': [],
        'Obligations': None
    }

    description = root.find('./{*}Description')
    if description is not None:
        description_text = description.text.strip()
        policy_dict['Description'] = parse_description(description_text)

    target = root.find('./{*}Target')
    for rule in root.findall('./{*}Rule'):
        policy_dict['Rules'].append(process_rule(rule))

    obligations_element = root.find('./{*}ObligationExpressions')
    if obligations_element is not None:
        policy_dict['Obligations'] = parse_obligations(obligations_element)

    return policy_dict

def evaluate_function(function_id, arguments, attributes):
    if function_id == 'urn:oasis:names:tc:xacml:1.0:function:string-equal':
        arg1 = evaluate_expression(arguments[0], attributes)
        arg2 = evaluate_expression(arguments[1], attributes)
        return arg1 == arg2
    elif function_id == 'urn:oasis:names:tc:xacml:1.0:function:string-one-and-only':
        return evaluate_expression(arguments[0], attributes)
    elif function_id == 'urn:oasis:names:tc:xacml:1.0:function:and':
        return all(evaluate_expression(arg, attributes) for arg in arguments)
    elif function_id == 'urn:oasis:names:tc:xacml:1.0:function:or':
        return any(evaluate_expression(arg, attributes) for arg in arguments)
    elif function_id == 'urn:oasis:names:tc:xacml:3.0:function:string-starts-with':
        arg1 = evaluate_expression(arguments[0], attributes)
        arg2 = evaluate_expression(arguments[1], attributes)
        return arg1.startswith(arg2)
    elif function_id == 'urn:oasis:names:tc:xacml:3.0:function:string-ends-with':
        arg1 = evaluate_expression(arguments[0], attributes)
        arg2 = evaluate_expression(arguments[1], attributes)
        return arg1.endswith(arg2)
    elif function_id == 'urn:oasis:names:tc:xacml:1.0:function:string-normalize-to-lower-case':
        arg = evaluate_expression(arguments[0], attributes)
        return arg.lower()
    else:
        raise NotImplementedError(f"Function {function_id} not implemented.")

def evaluate_expression(expression, attributes):
    if 'Apply' in expression:
        function_id = expression['FunctionId']
        arguments = expression['Arguments']
        return evaluate_function(function_id, arguments, attributes)
    elif 'AttributeDesignator' in expression:
        attribute_id = expression['AttributeDesignator']['AttributeId']
        return attributes.get(attribute_id)
    elif 'AttributeValue' in expression:
        return expression['AttributeValue']['Value']

def evaluate_condition(condition, attributes):
    if condition is None:
        return True
    if 'Apply' in condition:
        return evaluate_expression(condition['Apply'], attributes)

def evaluate_policy(policy_dict, attributes):
    rule_combining_alg = policy_dict['RuleCombiningAlgId']
    final_decision = 'NotApplicable'

    if rule_combining_alg.endswith('first-applicable'):
        for rule in policy_dict['Rules']:
            condition_result = evaluate_condition(rule['Condition'], attributes)
            if condition_result:
                final_decision = rule['Effect']
                policy_dict['Evaluation'] = {
                    'AppliedRuleId': rule['RuleId'],
                    'Decision': final_decision,
                    'ConditionResult': condition_result
                }
                break

    elif rule_combining_alg.endswith('permit-overrides'):
        permit_found = False
        deny_found = False
        applied_rules = []
        for rule in policy_dict['Rules']:
            condition_result = evaluate_condition(rule['Condition'], attributes)
            if condition_result:
                applied_rules.append({
                    'RuleId': rule['RuleId'],
                    'Effect': rule['Effect'],
                    'ConditionResult': condition_result
                })
                if rule['Effect'] == 'Permit':
                    permit_found = True
                elif rule['Effect'] == 'Deny':
                    deny_found = True
        if permit_found:
            final_decision = 'Permit'
        elif deny_found:
            final_decision = 'Deny'
        else:
            final_decision = 'NotApplicable'
        policy_dict['Evaluation'] = {
            'AppliedRules': applied_rules,
            'Decision': final_decision
        }

    elif rule_combining_alg.endswith('deny-overrides'):
        deny_found = False
        permit_found = False
        applied_rules = []
        for rule in policy_dict['Rules']:
            condition_result = evaluate_condition(rule['Condition'], attributes)
            if condition_result:
                applied_rules.append({
                    'RuleId': rule['RuleId'],
                    'Effect': rule['Effect'],
                    'ConditionResult': condition_result
                })
                if rule['Effect'] == 'Deny':
                    deny_found = True
                elif rule['Effect'] == 'Permit':
                    permit_found = True
        if deny_found:
            final_decision = 'Deny'
        elif permit_found:
            final_decision = 'Permit'
        else:
            final_decision = 'NotApplicable'
        policy_dict['Evaluation'] = {
            'AppliedRules': applied_rules,
            'Decision': final_decision
        }
    else:
        raise NotImplementedError(f"Rule Combining Algorithm {rule_combining_alg} not implemented.")

    return final_decision

def process_and_evaluate_policy_file(input_file, attributes):
    tree = ET.parse(input_file)
    root = tree.getroot()
    policy_dict = process_policy(root)
    access_decision = evaluate_policy(policy_dict, attributes)
    policy_dict['AccessDecision'] = access_decision
    return policy_dict

attribute_values = {
    'location-mobile': 'true'
}

input_files = [
    './parser/examples/xacml_policy.xacml',
    './parser/examples/xacml_policy2.xacml',
    './parser/examples/xacml_policy3.xacml',
    './parser/examples/xacml_policy4.xacml',
    './parser/examples/xacml_policy5.xacml'
]

output_dir = './parser/processed_policies'
os.makedirs(output_dir, exist_ok=True)

for input_file in input_files:
    policy = process_and_evaluate_policy_file(input_file, attribute_values)
    output_file = os.path.join(output_dir, f'processed_{os.path.basename(input_file).replace(".xacml", ".json")}')
    with open(output_file, 'w') as json_file:
        json.dump(policy, json_file, indent=4)
    print(f"Processed policy saved to {output_file}")
    print(f"Access Decision: {policy.get('AccessDecision')}")
