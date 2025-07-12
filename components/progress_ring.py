import plotly.graph_objects as go
import numpy as np

def create_progress_ring(hours, activity_name, target_hours=10000):
    """Create a progress ring showing hours completed out of target."""
    percentage = (hours / target_hours) * 100
    remaining = 100 - percentage
    
    # Create the donut chart
    fig = go.Figure(data=[
        go.Pie(
            values=[percentage, remaining],
            hole=0.7,
            marker_colors=['#22C55E', '#E5E7EB'],
            textinfo='none',
            hoverinfo='skip',
            showlegend=False
        )
    ])
    
    # Add center text
    fig.add_annotation(
        text=f"<b>{hours:.0f}h</b><br>{percentage:.1f}%<br><span style='font-size:14px'>{activity_name}</span>",
        x=0.5, y=0.5,
        font=dict(size=24, color='#1F2937'),
        showarrow=False,
        align='center'
    )
    
    # Update layout
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_mini_progress_ring(hours, activity_name, target_hours=10000):
    """Create a smaller progress ring for activity cards."""
    percentage = (hours / target_hours) * 100
    remaining = 100 - percentage
    
    fig = go.Figure(data=[
        go.Pie(
            values=[percentage, remaining],
            hole=0.6,
            marker_colors=['#16A34A', '#F3F4F6'],
            textinfo='none',
            hoverinfo='skip',
            showlegend=False
        )
    ])
    
    fig.add_annotation(
        text=f"<b>{hours:.0f}h</b>",
        x=0.5, y=0.5,
        font=dict(size=16, color='#1F2937'),
        showarrow=False
    )
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig 