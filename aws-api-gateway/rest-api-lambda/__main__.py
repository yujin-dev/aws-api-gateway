import pulumi

CONFIG = pulumi.Config()
is_proxy = CONFIG.require_bool("is_proxy")

############ setup ############
print("PROXY: ", is_proxy)
if is_proxy: 
    from proxy.integration import create_lambda_function, create_rest_proxy
    create_rest_proxy(create_lambda_function())
else:
    from non_proxy.integration import create_lambda_function, create_rest_non_proxy
    create_rest_non_proxy(create_lambda_function())