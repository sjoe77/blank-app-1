import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# HELP / DEFINITIONS
EQUITY_BALANCE= "The total capital available for investment."
EXPECTED_RETURN= "The multiplier by which an investment's value might grow or shrink. "
FRACTIONAL_KELLY= f"""The Kelly Criterion considers both the odds of a bet and 
the probability of winning to decide how much of your capital you should risk. The Fractional Kelly Criterion(we will use 33%)  is a risk management strategy derived from the full Kelly Criterion, 
which is used to determine the optimal size of a series of bets to maximize long-term growth of wealth"""
FRACTIONAL_KELLY_PERCENT= "Fractional Kelly (33%)"





def is_positive_number(value):
    if isinstance(value, (int, float)) and value > 0:
        return True
    return False

# Checks if all elements of a list are positive values > 0 or else return false
def all_positive_numbers(values):
    return all(is_positive_number(value) for value in values)

def is_number(value):
    if isinstance(value, (int, float)):
        return True
    return False

def all_is_number(values):
    return all(is_number(value) for value in values)

def format_currency(value):
    """
    Formats a number as currency with a dollar sign, comma as thousand separator,
    and suppresses trailing zeros after the decimal point.

    Parameters:
    - value (float or int): The amount to format as currency.

    Returns:
    - str: The formatted currency string.
    """
    # Format the number with two decimal places
    formatted_value = f"{value:,.2f}"
    
    # Remove unnecessary trailing zeros and decimal point if not needed
    formatted_value = formatted_value.rstrip('0').rstrip('.')
    
    # Add the dollar sign
    return f"${formatted_value}"

def format_percentage(value):
    """
    Formats a number as a percentage, suppressing trailing zeros after the decimal point.

    Parameters:
    - value (float): The number to format as a percentage.

    Returns:
    - str: The formatted percentage string.
    """
    percentage = value * 100
    return f"{percentage:.2f}".rstrip('0').rstrip('.') + "%"

def calculate():
    
    # Get input values from Session state
    equity_balance=st.session_state["equity_balance"]
    exp_return=st.session_state["exp_return"]
    prob_win=st.session_state["prob_win"] 
    prob_loss=100-st.session_state["prob_win"]
    stoploss_percent=st.session_state["stoploss_percent"]
    criteria=st.session_state["criteria"]
    print (f"Equity Balance = {equity_balance}")
    print (f"Exp return = {exp_return}")
    print (f"Prob Win - {prob_win}")
    print (f"Prob Loss - {prob_loss}")
    if  exp_return==0:
        st.session_state["worth_investing"]=False
        return
    if all_is_number([equity_balance,exp_return,prob_win,prob_loss]) and all_positive_numbers([equity_balance]) :
        kelly_percent = (((exp_return * prob_win/100) - prob_loss/100)/exp_return)
        kelly_percent = round(kelly_percent, 2)
        if criteria==FRACTIONAL_KELLY_PERCENT:
            kelly_percent=round(kelly_percent * .3333,2)
        position_kelly = kelly_percent * equity_balance
       
        print("Postion kelly=" + str(position_kelly))
        # Set if worth investing
        if (position_kelly <= 0):
            st.session_state["worth_investing"]=False
            return
        else:
            st.session_state["worth_investing"]=True

        pos_risk = position_kelly
        if stoploss_percent > 0:
            pos_risk=stoploss_percent * position_kelly/100 
        
        percent_risk_on_equity=(pos_risk/equity_balance)

        st.session_state["kelly_percent"]=format_percentage(kelly_percent)
        st.session_state["position_kelly"]=format_currency(position_kelly)
        st.session_state["pos_risk"]= format_currency(pos_risk)
        st.session_state["percent_risk_on_equity"]=format_percentage(percent_risk_on_equity)
        st.session_state["show_results"]=True
    else:
        st.session_state["show_results"]=False
        return

    print("Kelly Percent=" + str(kelly_percent))
    print("K=" +  st.session_state["position_kelly"])
    print("Percent Risk on Equity=" + str(percent_risk_on_equity) )

    # Dataframe for Pie chart
    cols=['labels','values']
    data = np.array([["Postion  ",position_kelly], ["Remaining Equity",equity_balance-position_kelly]])
    df = pd.DataFrame(data=data,  columns=cols)
    st.session_state["pie_df"]=df
   

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
    st.session_state["criteria"] = FRACTIONAL_KELLY_PERCENT

# Initialize imputs values for equity balance, win probaility when coming in first time
# This give user's a sample/example of how this works
if not len(st.session_state.keys()):
    st.session_state["equity_balance"] = 20000
    st.session_state["exp_return"] = 4
    st.session_state["prob_win"] = 60
    st.session_state["prob_loss"] = 40
    st.session_state["stoploss_percent"] = 10
    st.session_state["criteria"] = FRACTIONAL_KELLY_PERCENT
    calculate()


### Render UI###
st.header("An illustration of Kelly's criterion", help=FRACTIONAL_KELLY ,divider="blue")

#Inputs
criteria = st.radio("Criteria", ["Kelly", FRACTIONAL_KELLY_PERCENT], key="criteria", horizontal=True,label_visibility="hidden" ,on_change=calculate)
leftCol, rightCol = st.columns(2)
with leftCol:
    equity_balance = st.number_input("Equity balance", key="equity_balance", help=EQUITY_BALANCE,  on_change=calculate)
    prob_win = st.slider("Probability of winning", key="prob_win" , min_value=0, max_value=100, on_change=calculate)
    
with rightCol:
    exp_return = st.number_input("Expected return multiplier", key="exp_return",help=EXPECTED_RETURN, on_change=calculate)
    stoploss_percent = st.slider("Stop loss percentage", key="stoploss_percent", min_value=0, max_value=100, on_change=calculate) 



if st.session_state["show_results"]:
    st.subheader("Results", divider="blue")
    if st.session_state["worth_investing"]:
        c1, c2,c3 = st.columns(3)
        with c1:
            st.metric("Kelly's Recommended %", st.session_state["kelly_percent"], delta=None,  help="Kelly's recommendation for a percentage of equity to invest", )
            st.metric("Position risk", st.session_state["pos_risk"], delta=None,  help="Investment amount at risk taking into account a stop loss percentage", )
        with c2:
            st.metric("Recommended position size", st.session_state["position_kelly"], delta=None,  help="Investment amount recommened to invest using Kelly's criterion", )
            st.metric("Percent risk on equity", st.session_state["percent_risk_on_equity"], delta=None,  help="Investment amount as a percentage of available equity amount", )
        with c3:
            fig = px.pie(st.session_state["pie_df"],  values='values', names='labels', hole=0.7)
            fig.update_layout(legend=dict(x=1.5,y=0.5),margin=dict(l=75, r=75, t=10, b=10),width=600, height=300) 
            config={
                'displayModeBar': False
            }
            fig.update_traces(hovertemplate = "$%{value} (%{percent})", textposition='outside',texttemplate=' $%{value} (%{percent})') 
        st.plotly_chart(fig,  theme="streamlit", config=config) 
    else:
        
        st.warning("Not worth investing",icon="⚠️")
   


reset_btn_col, clear_btn_col = st.columns(2)

    
with reset_btn_col:
    st.button("Show me an example",on_click=reset)

with clear_btn_col:
    st.button("Clear",on_click=clear)




st.subheader("References", divider="blue")

st.markdown("""
                        
1. [Wikipedia - Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
2. [KELLY CRITERION | Ed Thorp | Optimal Position Sizing For Stock Trading](https://www.youtube.com/watch?app=desktop&v=THYLv5_0Vm8)


""")

st.markdown("**Disclaimer:** This calculator is provided for informational and educational purposes only. It is not intended to provide financial, investment, or legal advice. The results generated by this calculator are estimates based on the information provided and should not be relied upon for making any financial decisions. Consult with a qualified financial advisor or other professional for personalized advice tailored to your specific situation.")

