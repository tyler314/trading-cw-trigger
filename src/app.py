from dto.strategy import Dte1
from utils.common_utils import OrderType


def lambda_handler(event=None, context=None):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    return_code = {
        "statusCode": 200,
        "body": '"message": "SUCCESS"'
    }
    try:
        strategy = Dte1(ticker="SPX", order_type=OrderType.CREDIT, buying_power=500)
        print(strategy.execute())
    except Exception as e:
        return_code["statusCode"] = 400
        return_code["body"] = '"message": "{}"'.format(e)

    return return_code


if __name__ == '__main__':
    lambda_handler()
