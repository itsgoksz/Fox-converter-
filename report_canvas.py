import json
import streamlit as st

st.set_page_config(layout="wide")

with open("report_definition_banded.json") as f:
    report = json.load(f)

st.title(f"FoxPro Engine - {report['report_name']}")

# Conversion factor: FoxPro Report Units (1/10000 inch) to pixels (96 DPI)
SCALE = 96 / 10000.0

html = """
<div style="
position:relative;
width:1200px;
border:1px solid #ccc;
background:white;
color:black;
font-family: monospace;
margin-left: 120px;
">
"""

def render_band(band):
    band_height = (band["height"] * SCALE)
    
    # We create a relative container for the band
    band_html = f'''
    <div style="
        position: relative;
        width: 100%;
        height: {band_height}px;
        border-bottom: 1px dashed #eee;
    ">
    '''
    
    # Label to show which band it is (for visualizing the architecture)
    band_html += f'''
    <div style="position: absolute; top: 0; left: -110px; font-size: 10px; color: gray; width: 100px; text-align: right; padding-top: 5px; font-family: sans-serif;">
        <b>{band["name"]}</b>
    </div>
    '''
    
    for obj in band["objects"]:
        top = (obj["vpos"] * SCALE)
        left = (obj["hpos"] * SCALE)
        width = (obj["width"] * SCALE)
        height = (obj["height"] * SCALE)
        
        font_size = obj.get("fontsize")
        font_size_css = f"font-size: {font_size}pt;" if font_size and font_size > 0 else "font-size: 10px;"
        
        # Parse the display text for this object
        label = obj["expr"] if obj["expr"] and obj["expr"] != "None" else obj["name"]
        if not label or label == "None":
            label = ""
        
        # Determine styling based on FoxPro OBJTYPE
        border = "0px"
        bg_color = "transparent"
        
        # Default fallback for zero dimensions (mostly for text)
        if width == 0 and obj["objtype"] not in [6, 7]: width = 100
        if height == 0 and obj["objtype"] not in [6, 7]: height = 15

        if obj["objtype"] == 6: # Line
            label = ""
            bg_color = "black"
            if width == 0: 
                width = 1 # Vertical line
            if height == 0: 
                height = 1 # Horizontal line
        elif obj["objtype"] == 7: # Shape/Box
            border = "1px solid black"
            label = ""
        elif obj["objtype"] == 17: # Picture
            bg_color = "#f0f0f0"
            border = "1px dotted blue"
            label = "[PICTURE]"
            
        band_html += f"""
        <div style="
            position: absolute;
            top: {top}px;
            left: {left}px;
            width: {width}px;
            height: {height}px;
            {font_size_css}
            border: {border};
            background-color: {bg_color};
            overflow: hidden;
            white-space: nowrap;
            line-height: 1;
        ">
            {label}
        </div>
        """
        
    band_html += "</div>"
    return band_html

for band in report["bands"]:
    # Skip bands with zero height and no objects
    if band["height"] == 0 and len(band["objects"]) == 0:
        continue
        
    if band["name"] == "Detail":
        # Simulate repeating data rows!
        for i in range(5):
            html += render_band(band)
    else:
        # Render header/footer bands once
        html += render_band(band)

html += "</div>"

st.components.v1.html(html, height=1200, scrolling=True)
