from fastapi import APIRouter, HTTPException, Depends

from routers.users import get_current_user
from services.coin_service import get_coin_data, generate_graph
from models.coin import Coin
from models.user import User

router = APIRouter(prefix="/coins", tags=["Coins"])


@router.get("/", response_model=list[Coin])
def get_coins(current_user: User = Depends(get_current_user)):
    """Fetch details of all available coins."""
    data = get_coin_data()
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])

    return [Coin(symbol=item["symbol"], last_price=float(item["lastPrice"]),
                 price_change_percent=float(item["priceChangePercent"])) for item in data]


@router.get("/{symbol}", response_model=Coin)
def get_coin(symbol: str, current_user: User = Depends(get_current_user)):
    """Fetch details of a specific coin."""
    data = get_coin_data(symbol)
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    return Coin(
        symbol=data["symbol"],
        last_price=float(data["lastPrice"]),
        price_change_percent=float(data["priceChangePercent"])
    )


@router.get("/{symbol}/graph")
def get_coin_graph(symbol: str, current_user: User = Depends(get_current_user)):
    """Generate and return a graph for the selected coin."""
    data = generate_graph(symbol)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    return data
