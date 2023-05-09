import openai
from PIL import Image
import requests
from io import BytesIO
import streamlit as st
import time
import json
import random


st.title("YarnGen - Background Design Generator")
#st.write("This is a background design generator that uses OpenAI's API to generate background designs for your posts. You can either select the colors from the dropdown menu or enter the colors as text. After selecting the colors, select the type of background design you want to generate. You can also select the number of background designs to generate and the size of the background design. Finally, enter your API key and click on the 'Generate Background Design' button to generate the background design.")
with st.sidebar:
    st.title("YarnGen")
    st.subheader("Background Design Generator")

    st.write("Enter your API key")
    openai_key = st.text_input("API Key: ",placeholder = "Enter your API key here")
    st.write("---------------------------------------------")

    st.write("Choose how do you want to generate the background designs")
    input = st.radio("Input",("Use pre-selected filters","Use free-form text"),label_visibility="hidden",horizontal=True)
    #use_freeform_text = st.checkbox("Use free-form text",key = "prompt")
    #use_preselected_filters = st.checkbox("Use pre-selected filters",key = "filters")
    st.write("---------------------------------------------")

    if input == "Use free-form text":
        freeform_text_input = st.text_input("Enter your free-form text",placeholder = "a background with a white brick wall with a faded, distressed look")
        st.write("---------------------------------------------")

    if input == "Use pre-selected filters":
        st.write("Select the colors of the background design")
        color_choice = st.multiselect("Colors", ("red", "sky blue", "green", "yellow", "orange", "purple", "pink", "black", "white", "gray", "brown", "cyan", "magenta", "teal", "lime", "maroon", "navy", "olive", "silver", "violet", "beige", "gold", "khaki", "lavender", "orchid", "plum", "salmon", "tan", "turquoise", "white"),("yellow"),max_selections=3)
        add_text_for_color = st.checkbox("Not in the list? Add color as text.",key = "color")
        if add_text_for_color:
            color_choice = [st.text_input("Add color suggestions here",placeholder = "Bluish green")]
        st.write("You selected:", color_choice)
        st.write("---------------------------------------------")

        st.write("Select the type of background design")
        design_choice = st.selectbox("Background Design Types",("Gradient","Solid colour","Themes"))

        if design_choice == "Solid colour":
            if len(color_choice)>1:
                split_type = st.selectbox("Select split", ("horizontally","vertically"))

        if design_choice == "Gradient":
            sub_design = st.selectbox("Select sub-type", ("Simple gradient","Texture gradient","Floral pattern gradients","Blurred gradient","Polka dot pattern gradients","Plaid pattern gradients","Herringbone pattern gradients","Chevron pattern gradients","Spiral Gradient","Radial Gradient","Angular Gradient pattern","Diamond Gradient pattern","Rectangular gradient pattern","Geometric gradient pattern", "Abstract pattern gradients"))

        if design_choice == "Themes":
            sub_theme = st.selectbox("Select sub-type", ("Galaxy","Bubbles","Trees","Nature","Minimalist wall","Mossy rocks","Sun dappled leaves","Ocean","Cityscape"))

        add_text_for_design_type = st.checkbox("Not in the list? Add design suggestions as text.",key = "design")
        if add_text_for_design_type:
            design_choice = st.text_input("Add design suggestions here",placeholder = "weathered wood texture")
            st.write("You selected:", design_choice)
        st.write("---------------------------------------------")

    num = st.slider("Select the number of background designs to generate", 1, 10, 3)
    st.write("---------------------------------------------")

    size_choice = st.radio("Select the size of the background design", ( "1024x1024","512x512","256x256"))
    st.write("You selected:", size_choice)
    st.write("---------------------------------------------")

    clicked = st.button("Generate Background Designs")

def prompt_builder_for_freeform(freeform_text_input):
    prompt = f"Generate {freeform_text_input}"
    return prompt

def get_random_description(theme):
    with open('themes.json') as f:
        themes = json.load(f)

    if theme not in themes:
        return f"a random background theme"

    descriptions = themes[theme]
    return random.choice(descriptions)

def prompt_builder_for_preselected_filters(color_choice,design_choice,split ='horizontally',sub_theme="random background"):
    if design_choice == "Solid colour":
        background_colour_str = ", ".join(color_choice)
        prompt = f"Generate a {design_choice} background with colours {background_colour_str}. Split {split} exactly by {len(color_choice)}."
    elif design_choice == "Themes":
        theme_description = get_random_description(sub_theme)
        prompt = f"Generate {theme_description}"
    else:
        if len(color_choice)>1:
            background_colour_str = ", ".join(color_choice)
            prompt = f"Generate a high resolution {design_choice} background with colours {background_colour_str}"
        else:
            prompt = f"Generate a high resolution {design_choice} background with the colour {color_choice[0]}"
    return prompt
    

if clicked:
    if len(openai_key) > 1:
        openai.api_key = openai_key
        st.write("Generating background design...")
        time.sleep(2)
        my_bar = st.progress(0)
        if input == "Use free-form text":
            prompt = prompt_builder_for_freeform(freeform_text_input)
        if input == "Use pre-selected filters":
            if design_choice == "Solid colour":
                if len(color_choice)>1:
                    prompt = prompt_builder_for_preselected_filters(color_choice,design_choice,split=split_type)
                else:
                    prompt = prompt_builder_for_preselected_filters(color_choice,design_choice)
            elif design_choice == "Themes":
                prompt = prompt_builder_for_preselected_filters(color_choice,design_choice,sub_theme=sub_theme)
            elif design_choice == "Gradient":
                prompt = prompt_builder_for_preselected_filters(color_choice,design_choice=sub_design)
            else:
                prompt = f"Generate a background for {design_choice}"
        st.write(prompt)
        response = openai.Image.create(
        prompt=prompt,
        n=num,
        size=size_choice
        )
        data = response['data']
        try:
            with st.container():
                for ind,res in enumerate(data):
                    url = res['url']
                    response = requests.get(url)
                    img = Image.open(BytesIO(response.content))
                    #rotated_image = img.rotate(90)
                    #img.save('/Users/aadithyuenair/Documents/Projects/yarnit/knowledge-graph-api/images/{}-{}.png'.format(prompt,ind))
                    st.image(img, caption='{}-{}'.format(prompt,ind), use_column_width=True)
                    btn = st.download_button(
                                                label="Download image",
                                                data=BytesIO(response.content),
                                                file_name='{}-{}.png'.format(prompt,ind), 
                                                mime="image/png"
                                            )
                    #st.download_button(label="Download", data=img, file_name='{}-{}.png'.format(prompt,ind), mime='application/octet-stream')
                    my_bar.progress((ind+1)/num)
        except Exception as e:
            st.write(e)
            st.error('Please enter a valid API key!', icon="🚨") 
    else:
        st.error('Please enter an API key!', icon="🚨")
