import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  # Import for go.Funnel
import os
import base64
import config


def display_app_header():
    """Displays the main application header with an optional logo."""
    # This function remains unchanged.
    if os.path.exists(config.LOGO_PATH):
        with open(config.LOGO_PATH, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div class=\"header\">
                Timo Digital Bank Dashboard <img src='data:image/png;base64,{encoded_image}' width='40' style='image-rendering: auto; margin-left: 0.1em;'/>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class=\"header\">
                Timo Digital Bank Dashboard 🏦
            </div>
            """, unsafe_allow_html=True
        )


def metric_card(title: str, value: str):
    """Displays a custom styled metric card."""
    # This function remains unchanged.
    st.markdown(f"""
        <div class="metric-card">
            <div class="card-header">{title}</div>
            <p>{value}</p>
        </div>
    """, unsafe_allow_html=True)


def plot_line_chart(df, x, y, title, x_label, y_label):
    """Generates and displays a Plotly line chart."""
    # This function remains unchanged.
    if df.empty:
        st.warning(f"No data to display for '{title}'.")
        return

    fig = px.line(
        df, x=x, y=y, title=title, labels={x: x_label, y: y_label},
        template="plotly_white", line_shape="spline"
    )
    fig.update_layout(
        hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color="#333", title_font_size=24, title_font_color="#1a2a3a",
        margin=dict(l=40, r=40, t=80, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_bar_chart(df, x, y, title, x_label, y_label, color_column=None, color_map=None, text_column=None):
    """Generates and displays a Plotly bar chart with optional text labels."""
    if df.empty:
        st.warning(f"No data to display for '{title}'.")
        return

    px_kwargs = {
        "x": x, "y": y, "title": title, "labels": {x: x_label, y: y_label},
        "template": "plotly_white",
    }
    if color_column:
        px_kwargs["color"] = color_column
        if color_map:
            px_kwargs["color_discrete_map"] = color_map
        else:
            px_kwargs["color_discrete_sequence"] = px.colors.qualitative.Pastel
    if text_column:
        px_kwargs["text"] = text_column

    fig = px.bar(df, **px_kwargs)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#333",
        title_font_size=24, title_font_color="#1a2a3a", margin=dict(l=40, r=40, t=80, b=40)
    )
    if text_column:
        fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


def plot_pie_chart(df, values, names, title, hole=0.4, color_column=None, color_map=None):
    """Generates and displays a Plotly pie chart."""
    # This function remains unchanged.
    if df.empty:
        st.warning(f"No data to display for '{title}'.")
        return

    px_kwargs = {
        "values": values, "names": names, "title": title,
        "template": "plotly_white", "hole": hole,
    }
    if color_column:
        px_kwargs["color"] = color_column
        if color_map:
            px_kwargs["color_discrete_map"] = color_map
        else:
            px_kwargs["color_discrete_sequence"] = px.colors.qualitative.Pastel

    fig = px.pie(df, **px_kwargs)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#333",
        title_font_size=24, title_font_color="#1a2a3a", margin=dict(l=40, r=40, t=80, b=40),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", yanchor="top"), height=500
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(df))
    st.plotly_chart(fig, use_container_width=True)


def plot_heatmap(df_pivot, title, x_label, y_label):
    """Generates and displays a Plotly heatmap from a pivot table."""
    # This function remains unchanged.
    if df_pivot.empty:
        st.warning(f"No data to display for '{title}'.")
        return

    fig = px.imshow(
        df_pivot, labels=dict(x=x_label, y=y_label, color="Count"),
        x=df_pivot.columns, y=df_pivot.index, text_auto=True, aspect="auto",
        color_continuous_scale="Viridis", title=title
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#333",
        title_font_size=24, title_font_color="#1a2a3a", margin=dict(l=40, r=40, t=80, b=40),
        xaxis_nticks=24
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_funnel_chart(df, x, y, title):
    """Generates and displays a Plotly funnel chart."""
    if df.empty:
        st.warning(f"No data to display for '{title}'.")
        return

    fig = go.Figure(go.Funnel(  #
        y=df[y],  #
        x=df[x],  #
        textinfo="value+percent initial"  #
    ))
    fig.update_layout(
        title_text=title,  #
        title_x=0.5,  #
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#333",
        title_font_size=24, title_font_color="#1a2a3a", margin=dict(l=40, r=40, t=80, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
