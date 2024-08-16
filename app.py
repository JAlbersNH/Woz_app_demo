from PyPDF2 import PdfReader
import streamlit as st
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
import pyautogui
import streamlit.components.v1 as components


# Load environment variables
# load_dotenv()


# for key in st.session_state.keys():
#     print(st.session_state[key], key)

file_path = 'documents/Grieven.xlsx'

# Read the first column, skip the first row
first_column = pd.read_excel(file_path, usecols=[0], skiprows=1)


# Convert the column to a list
grieven = first_column.squeeze().tolist()


st.set_page_config(
    page_title="Woz-App",
    page_icon='Images/logo.png',
    layout="wide",
    initial_sidebar_state= "expanded"
)

sidebar_logo = 'Images\Logo_transparant.png'
main_body_logo = 'Images\Logo_transparant.png'

st.logo(sidebar_logo, icon_image=main_body_logo)

st.markdown(
    r"""
    <style>
    .stDeployButton {
        visibility: hidden;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    MainMenu {visibility: hidden; }
    footer {visibility: hidden;}

    img[data-testid="stLogo"] {
            height: 7rem;
    }
    </style>
    """, unsafe_allow_html=True
)

main_tekst_container = st.empty()
if 'grief1' not in st.session_state:
    col1,col2, col3 = st.columns([0.5,2,1])
else:
    col1,col2, col3 = st.columns([2,0.5,1])



with col3:
    st.markdown("<h1 style='text-align: left; color: black;'>Woz autoresponder</h1>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px; line-height:1.6; color:#4a4a4a; text-align:left;'> De WOZ Autoresponder is speciaal ontworpen voor beoordelaars van WOZ-bezwaren. Met deze app kunnen beoordelaars eenvoudig de ingediende documenten, zoals bezwaarbrieven en ondersteunend bewijs, uploaden.<br><br>De ingebouwde AI analyseert de documenten grondig en distilleert automatisch de meest relevante informatie. Zo kan sneller worden bepaald of een bezwaar gegrond is of niet.<br><br>De app toont verzamelt all informatie voor elk bezwaar zoals fotos, omschrijvingen en uitspraken van de rechtbank. Nadat de beoordelaar een conclusie heeft geregistreerd bij elke grief helpt de app ook bij het opstellen van een reactie brief. Deze moet dan alleen nog kort nagelezen te worden voordat het process kan worden gesloten.<br><br><br><br></div>", unsafe_allow_html=True)
    

def main():
    if 'grief1' not in st.session_state:
        if 'OPENAI_API_KEY' not in os.environ:
            with st.sidebar:
                api_key = st.chat_input('Input a valid open ai api key', key='OPENAI_API_KEY')
                if api_key: 
                    os.environ['OPENAI_API_KEY'] = api_key

        with col3:
            with st.empty():
                
                pdf = st.file_uploader('Upload een bezwaar of gehoor brief ', type='pdf' )

                if pdf is not None:
                    pdf_reader = PdfReader(pdf)
                    # Text variable will store the pdf text
                    text = ""
                    with st.spinner('Onze AI is hard aan het werk...'):
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                        with open('documents/sample_grieven_response.txt') as tekst:
                            sample_grieven_response = tekst.read()
                            print('---------------------------------------')
                            print(sample_grieven_response)
                            print('---------------------------------------')



                            query = f'Haal alleen de paragrafen waarin bezwaar wordt gemaakt uit deze brief en neem ze woord voor woord over: {text}. Maak dan een bullet list waarin elke paragraaf wordt gekoppeld aan het best passende item in deze lijst: {grieven}. Geef je antwoord in de vorm: item in lijst - bijpassende paragraaf. dus het moet er zo uitzien: {sample_grieven_response}'
                            print(query)
                        client = OpenAI()

                        response = client.chat.completions.create(
                        model="gpt-4o",
                        # response_format={ "type": "json_object" },
                            messages=[
                                {"role": "user",
                                "content": query}
                            ]
                        )
                    
                    #with col1:
                        #binary_data = pdf.getvalue()
                        #pdf_viewer(input=binary_data, height=800)
                    #with col1:
                    with col2:
                        binary_data = pdf.getvalue()
                        pdf_viewer(input=binary_data, height=1000)
                    # with st.container(height=800):
                    #     st.write(response.choices[0].message.content)

                    with st.sidebar:
                        with st.container():
                            grievendict = {}
                            # print(response.choices[0].message.content)

                            # Process each line in the input data
                            for line in response.choices[0].message.content.strip().splitlines():
                                try:
                                    # Split by the first hyphen
                                    key_part, value = line[1:].split(' - ', 1)
                                    
                                    try:
                                        # Extract the final key and value by splitting again by the last hyphen
                                        key, value = value.rsplit(' - ', 1)
                                        
                                        # Clean up any extra spaces
                                        key = key.strip()
                                        
                                        # Combine the key with the first part to make the full key
                                        full_key = f"{key_part.strip()} - {key}"
                                    except:
                                        full_key = key_part.strip()

                                    value = value.strip().strip('"')
                                    # Add to dictionary
                                    grievendict[full_key] = value
                                except:
                                    print(f"This line did not work: {line}")

                            st.session_state['keys'] = grievendict.keys()

                            with st.form("grief_selectie", border=False):
                                components.html(
                                """

                                <script>
                                const inputs = window.parent.document.querySelectorAll('input');
                                inputs.forEach(input => {
                                    input.addEventListener('keydown', function(event) {
                                        if (event.key === 'Enter') {
                                            event.preventDefault();
                                        }
                                    });
                                });
                                </script>
                                """,
                                height=0
                                )
                                st.markdown("<div style='font-size:18px; line-height:1.6; color:#4a4a4a; text-align:left;'><strong>Selecteer de gegronde grieven:</strong> <br></div>", unsafe_allow_html=True)
                                vals =[]
                                comments=[]
                                for x in range(len(grievendict.keys())):

                                    with st.container(border=True):
                                        vals.append(st.checkbox(label=f"{list(grievendict.keys())[x]}", value=0, key = f'grief{x}'))
                                        st.write(grievendict[f"{list(grievendict.keys())[x]}"])
                                        comments.append(st.text_input(label = 'Opmerkingen', key = f'opmerking_grief{x}'))

                                nieuwe_woz_input = st.number_input(label ='Nieuwe WOZ in euros', min_value= 100000, max_value=10000000,step=10000, value = 500000, key='nieuwe_woz')
                                wrap_up_button = st.form_submit_button("Genereer reactie")
                                

    else: 
        gegrond = []
        ongegrond = []
        opmerkingen_dict = {}
        for i, grief in enumerate(st.session_state['keys']):
            if st.session_state[f'grief{i}'] == 1:
                gegrond.append(grief)
            elif st.session_state[f'grief{i}'] == 0:
                ongegrond.append(grief)
            opmerkingen_dict[f'{grief}'] = st.session_state[f'opmerking_grief{i}']
        # with sidebar_container.container():
        #     with st.container(border=True):
        #         st.write('Gegrond bevonden grieven')
        #         for i in gegrond:
        #             st.markdown("- " + i)

        #     with st.container(border=True):
        #         st.write('Ongegrond bevonden grieven')
        #         for i in ongegrond:
        #             st.markdown("- " + i)
              
        if gegrond == []:
            gegrond = "Geen"
        if ongegrond == []:
            ongegrond = "Geen"

        with col1:
            with st.spinner('De brief wordt geschreven...'):
                with open('documents/sample_reply.txt') as tekst:
                    reply_template = tekst.read()

                    client = OpenAI()
                    
                    query = f'Je werkt bij de gemeente rotterdam en reageert op een woz waarde bezwaar. Gebruik dit template en hou dezelfde structuur aan. Data, namen en adressen moeten worden vervangen door ["Data"], ["Naam"], ["Address"]: {reply_template} Je reactie moet de volgende gegronde grieven behandelen: {gegrond}. En deze ongegronde grieven {ongegrond}. Geef bij elke grief een uitleg van een paar zinnen, gebruik daarbij de bijpassende opmerking uit deze dictionary:{opmerkingen_dict}. Vervang het stuk waarin vergelijkbare huizen worden gebruikt door ["data van vergelijkbare huizen"]. De nieuwe WOZ waarde is vastgesteld op: {st.session_state['nieuwe_woz']}'
                    print(query)
                    client = OpenAI()

                    response = client.chat.completions.create(
                    model="gpt-4o",
                    # response_format={ "type": "json_object" },
                        messages=[
                            {"role": "user",
                            "content": query}
                        ]
                    )
                st.title('Antwoord template:')
                download = st.download_button('Download', response.choices[0].message.content)  # Defaults to 'text/plain'

                st.write(response.choices[0].message.content)
                with st.sidebar:
                    restart = st.button('Restart')        
                    if restart:
                        pyautogui.hotkey("ctrl","F5")                   
            
if __name__ == "__main__":
    main()