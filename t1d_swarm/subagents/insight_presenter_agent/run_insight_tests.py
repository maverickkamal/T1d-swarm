

import asyncio

from agent import run_presenter_with_single_forecast

from test_forecasts import (
    mock_forecast_stable,
    mock_forecast_hyper,
    mock_forecast_hypo,
    mock_forecast_erratic,
    mock_forecast_missing,
   
)

async def main():
    print("=== Running Insight Presenter Tests ===\n")

    print(">>> Test 1: Stable Scenario <<<")
    await run_presenter_with_single_forecast(mock_forecast_stable)

    print(">>> Test 2: Potential Hyperglycemia <<<")
    await run_presenter_with_single_forecast(mock_forecast_hyper)

    print(">>> Test 3: Potential Hypoglycemia <<<")
    await run_presenter_with_single_forecast(mock_forecast_hypo)

    print(">>> Test 4: Erratic Readings / Data Quality Issue <<<")
    await run_presenter_with_single_forecast(mock_forecast_erratic)

    print(">>> Test 5: Missing Data Scenario <<<")
    await run_presenter_with_single_forecast(mock_forecast_missing)

    # If you have additional mocks like mock_forecast_stress, un-comment:
    # print(">>> Test 6: Stress Scenario <<<")
    # await run_presenter_with_single_forecast(mock_forecast_stress)
    #
    # etc…

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            print("If running in a Jupyter/Colab notebook, use: await main()")
        else:
            raise
