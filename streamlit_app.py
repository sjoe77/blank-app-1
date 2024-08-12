import streamlit as st


# HELP / DEFINITIONS
EQUITY_BALANCE= "The total capital available for investment."
EXPECTED_RETURN= "The multiplier by which an investment's value might grow or shrink. "
FRACTIONAL_KELLY= f"The Fractional Kelly Criterion is a risk management strategy derived from the full Kelly Criterion, which is used to determine the optimal size of a series of bets to maximize long-term growth of wealth. The Kelly Criterion considers both the odds of a bet and the probability of winning to decide how much of your capital you should risk."

st.header("An illustration of Fractional Kelly's criterion", help=FRACTIONAL_KELLY ,divider="gray")



def is_positive_number(value):
    if isinstance(value, (int, float)) and value > 0:
        return True
    return False

# Checks if all elements of a list are positive values > 0 or else return false
def all_positive_numbers(values):
    return all(is_positive_number(value) for value in values)


def format_currency(amount):
    """
    Formats a number as currency with a dollar sign and comma as a thousand separator.

    Parameters:
    - amount (float or int): The amount of money to format.

    Returns:
    - str: The formatted currency string.
    """
    if not isinstance(amount, (int, float)):
        raise ValueError("Amount must be an integer or float.")
    
    # Format the number with commas and two decimal places
    formatted_amount = f"${amount:,.2f}"
    return formatted_amount

def calculate():
    # Get input values from Session state
    equity_balance=st.session_state["equity_balance"]
    exp_return=st.session_state["exp_return"]
    prob_win=st.session_state["prob_win"] 
    prob_loss=100-st.session_state["prob_win"]
    stoploss_percent=st.session_state["stoploss_percent"]

    if all_positive_numbers([equity_balance,exp_return,prob_win,prob_loss]):
        kelly_percent = (((exp_return * prob_win/100) - prob_loss/100)/exp_return)
        rounded_kelly_percent = round(kelly_percent, 2)
        print("Rounded Kelly Percent=" + str(rounded_kelly_percent))
        position_kelly = rounded_kelly_percent * equity_balance
        position_fractional_kelly =   position_kelly * .3333
        
        # Set if worth investing
        if (position_fractional_kelly <0):
            st.session_state["worth_investing"]=False
        else:
            st.session_state["worth_investing"]=True

        pos_risk = position_fractional_kelly
        if stoploss_percent > 0:
            pos_risk=stoploss_percent * position_fractional_kelly/100 
        
        percent_risk_on_equity=(pos_risk/equity_balance)
        st.session_state["position_kelly"]=format_currency(position_kelly)
        st.session_state["position_fractional_kelly"]= format_currency(position_fractional_kelly)
        print("K=" +  st.session_state["position_kelly"])
        print("FK=" +  st.session_state["position_fractional_kelly"])
        print("Percent Risk on Equity=" + str(percent_risk_on_equity) )
        st.session_state["pos_risk"]= format_currency(pos_risk)
        st.session_state["percent_risk_on_equity"]="{:.2%}".format(percent_risk_on_equity)
        st.session_state["show_results"]=True
    else:
        st.session_state["show_results"]=False

def reset():
    # Delete all the items in Session state
    for key in st.session_state.keys():
        del st.session_state[key]

def clear():
    # Delete all the items in Session state
    for key in st.session_state.keys():
        st.session_state[key]=None
    st.session_state["prob_win"] = 50
    st.session_state["stoploss_percent"] = 10

# Initialize imputs values for equity balance, win probaility when coming in first time
# This give user's a sample/example of how this works
if not len(st.session_state.keys()):
    st.session_state["equity_balance"] = 20000
    st.session_state["exp_return"] = 4
    st.session_state["prob_win"] = 60
    st.session_state["prob_loss"] = 40
    st.session_state["stoploss_percent"] = 10
    calculate()

#Inputs
leftCol, rightCol = st.columns(2)
with leftCol:
    equity_balance = st.number_input("Equity balance", key="equity_balance", help=EQUITY_BALANCE,  on_change=calculate)
    prob_win = st.slider("Probability of winning", key="prob_win" , min_value=0, max_value=100, on_change=calculate)
    
with rightCol:
    exp_return = st.number_input("Expected return multiplier", key="exp_return",help=EXPECTED_RETURN, on_change=calculate)
    stoploss_percent = st.slider("Stop loss percentage", key="stoploss_percent", min_value=0, max_value=100, on_change=calculate) 



if st.session_state["show_results"]:
    st.subheader("Results", divider="orange")
    if st.session_state["worth_investing"]:
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Recommended position size", st.session_state["position_fractional_kelly"], delta=None,  help="None", )
        with r2:
            st.metric("Position risk", st.session_state["pos_risk"], delta=None,  help="None", )
        with r3:
            st.metric("Percent risk on equity", st.session_state["percent_risk_on_equity"], delta=None,  help="None", )
    else:
        
        st.warning("Not worth investing",icon="⚠️")
   


reset_btn_col, clear_btn_col = st.columns(2)

    
with reset_btn_col:
    st.button("Show me an example",on_click=reset)

with clear_btn_col:
    st.button("Clear",on_click=clear)
    

st.markdown("**Disclaimer:** This calculator is provided for informational and educational purposes only. It is not intended to provide financial, investment, or legal advice. The results generated by this calculator are estimates based on the information provided and should not be relied upon for making any financial decisions. Consult with a qualified financial advisor or other professional for personalized advice tailored to your specific situation.")

