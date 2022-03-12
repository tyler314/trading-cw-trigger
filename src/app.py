from strategies.dte1_ic import Dte1IC
from utils.common_utils import OrderType
import watchtower
import logging

logging.basicConfig(level=logging.INFO, handlers=[watchtower.CloudWatchLogHandler()])
logger = logging.getLogger(__name__)


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

    try:
        strategy = Dte1IC(ticker="SPX", order_type=OrderType.CREDIT, buying_power=500, friday_quantity=2)
        response = strategy.execute()
        logging.info(str(response))
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    lambda_handler()
