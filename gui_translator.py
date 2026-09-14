import os
import json
import threading
import time
import re
import ast
import customtkinter as ctk
from tkinter import filedialog
import srt
from google import genai
from google.genai import types

# ----------------- GUI Settings -----------------
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# Safe persistent config path
CONFIG_DIR = os.path.expanduser("~/.config/ai-srt-translator")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class TranslatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SRT Translator - AI Powered")
        self.geometry("600x750")  # Slightly taller to fit new elements
        self.resizable(False, False)
        
        # Try loading native Linux window icon
        try:
             import PIL.Image as Image
             import PIL.ImageTk as ImageTk
             icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
             if os.path.exists(icon_path):
                 img = ImageTk.PhotoImage(Image.open(icon_path))
                 self.wm_iconphoto(True, img)
        except Exception:
             pass

        self.file_path = None
        self.is_translating = False
        
        self.config_data = self.load_config()
        self.create_widgets()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
             try:
                 with open(CONFIG_FILE, 'r') as f:
                     return json.load(f)
             except Exception:
                 return {}
        return {}
        
    def save_config(self, data):
        try:
            with open(CONFIG_FILE, 'w') as f:
                 json.dump(data, f)
        except Exception as e:
            print(f"Failed to save config: {e}")
             
    def create_widgets(self):
        # --- Header ---
        self.title_label = ctk.CTkLabel(self, text="AI Subtitle Translator", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        # --- API Key Section ---
        self.api_frame = ctk.CTkFrame(self)
        self.api_frame.pack(pady=10, padx=20, fill="x")
        
        self.api_label = ctk.CTkLabel(self.api_frame, text="Google Gemini API Key:", font=ctk.CTkFont(size=14))
        self.api_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="AIzaSy... Paste your key here.", show="*", width=400)
        self.api_entry.pack(padx=10, pady=(5, 10), fill="x")
        
        saved_key = self.config_data.get("api_key", "")
        if saved_key:
             self.api_entry.insert(0, saved_key)
             
        # --- Model Section ---
        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.pack(pady=10, padx=20, fill="x")
        
        self.model_label = ctk.CTkLabel(self.model_frame, text="AI Engine Model:", font=ctk.CTkFont(size=14))
        self.model_label.pack(side="left", padx=10, pady=10)
        
        saved_model = self.config_data.get("model", "gemini-3.6-flash")
        valid_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        if saved_model not in valid_models:
             saved_model = "gemini-3.6-flash"
        
        self.model_var = ctk.StringVar(value=saved_model)
        self.model_dropdown = ctk.CTkOptionMenu(
            self.model_frame, 
            values=valid_models,
            variable=self.model_var
        )
        self.model_dropdown.pack(side="right", padx=10, pady=10)

        # --- Target Language Section ---
        self.lang_frame = ctk.CTkFrame(self)
        self.lang_frame.pack(pady=10, padx=20, fill="x")
        
        self.lang_label = ctk.CTkLabel(self.lang_frame, text="Target Language:", font=ctk.CTkFont(size=14))
        self.lang_label.pack(side="left", padx=10, pady=10)
        
        saved_lang = self.config_data.get("target_language", "Polish")
        self.lang_var = ctk.StringVar(value=saved_lang)
        self.lang_dropdown = ctk.CTkOptionMenu(
            self.lang_frame, 
            values=["Polish", "English", "Spanish", "German", "French", "Italian", "Portuguese", "Dutch", "Russian", "Swedish", "Norwegian", "Danish", "Finnish", "Czech", "Slovak", "Hungarian", "Romanian", "Greek", "Turkish", "Ukrainian"],
            variable=self.lang_var
        )
        self.lang_dropdown.pack(side="right", padx=10, pady=10)
        
        # --- File Selection ---
        self.file_btn = ctk.CTkButton(self, text="Select Subtitles File (.srt)", font=ctk.CTkFont(size=16), height=50, fg_color="#F39C12", hover_color="#D68910", command=self.select_file)
        self.file_btn.pack(pady=20, padx=40, fill="x")
        
        self.file_label = ctk.CTkLabel(self, text="No file selected", text_color="gray")
        self.file_label.pack()

        # --- Log Console ---
        self.log_textbox = ctk.CTkTextbox(self, height=140, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.pack(pady=10, padx=20, fill="x")
        self.log_textbox.configure(state="disabled")
        self.log("Welcome! Attach a file and start the magic.\nReady.")

        # --- Progress Bar and Start Button ---
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=10, padx=40, fill="x")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(self, text="Progress: 0%")
        self.progress_label.pack()

        self.start_btn = ctk.CTkButton(self, text="START TRANSLATION", font=ctk.CTkFont(size=18, weight="bold"), height=50, command=self.start_translation)
        self.start_btn.pack(pady=(10, 20), padx=40, fill="x")

    def log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end") 
        self.log_textbox.configure(state="disabled")

    def select_file(self):
        if self.is_translating:
            return
            
        import subprocess
        try:
            # Try native Ubuntu/GNOME file picker via Zenity
            result = subprocess.run(
                ['zenity', '--file-selection', '--title=Select subtitles file', '--file-filter=*.srt'], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                path = result.stdout.strip()
            else:
                path = ""
        except FileNotFoundError:
            # Fallback to tkinter if Zenity is missing
            filetypes = (("SRT Files", "*.srt"), ("All files", "*.*"))
            path = filedialog.askopenfilename(title="Select subtitles file", filetypes=filetypes)
        
        if path:
            self.file_path = path
            self.file_label.configure(text=f"Selected: {os.path.basename(path)}", text_color="white")
            self.log(f"Target file loaded: {os.path.basename(path)}")

    def start_translation(self):
        if not self.file_path:
            self.log("[Error] Please select an .srt file first!")
            return
            
        api_key_input = self.api_entry.get().strip()
        if not api_key_input:
            self.log("[Error] You must provide a Gemini API Key.")
            return

        target_lang = self.lang_var.get().strip()

        # Update local config memory
        self.config_data["api_key"] = api_key_input
        self.config_data["model"] = self.model_var.get()
        self.config_data["target_language"] = target_lang
        self.save_config(self.config_data)

        self.is_translating = True
        self.start_btn.configure(state="disabled", text="TRANSLATING...", fg_color="gray")
        self.file_btn.configure(state="disabled")
        
        self.log("\n>>> Initializing translator thread...")
        self.progress_bar.set(0)
        
        thread = threading.Thread(target=self.run_translator_logic, args=(api_key_input, target_lang))
        thread.daemon = True
        thread.start()

    def translate_batch(self, core_client, model_name, texts, target_language, max_retries=5):
        user_prompt = json.dumps(texts, ensure_ascii=False)
        system_instruction = f"You are a professional movie subtitle translator.\nTranslate very naturally and colloquially to {target_language}, preserving the emotional charge of the original dialogue. Auto-detect the primary original language.\nStrictly preserve all HTML formatting (<i>, <b>, etc.).\nIMPORTANT: You MUST return exactly as many translations as the input array length ({len(texts)} items). Do not merge, combine, or split lines. Maintain a strict 1:1 mapping.\nThe output MUST BE a 100% valid JSON object mapped to the key 'translations'."

        safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        ]
        
        for attempt in range(max_retries):
            try:
                response = core_client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.3,
                        safety_settings=safety_settings
                    )
                )
                
                result_text = response.text
                if result_text is None:
                     raise Exception("Received empty text (NoneType) from Server.")
                
                parsed_list = []
                
                # Safeguard for API explicitly returning dict
                if isinstance(result_text, dict):
                    parsed_list = result_text.get("translations", [])
                else:
                    try:
                        # Clean up random model wrappers
                        if isinstance(result_text, str):
                            clean_text = re.sub(r'```(?:json)?|```', '', result_text).strip()
                            
                            start_idx = clean_text.find('{')
                            end_idx = clean_text.rfind('}')
                            if start_idx != -1 and end_idx != -1:
                                clean_text = clean_text[start_idx:end_idx+1]
                            
                            result = json.loads(clean_text)
                            parsed_list = result.get("translations", [])
                        else:
                            raise Exception("Unsupported variable type of response.text")
                            
                    except Exception as json_err:
                        self.log(f"[Model Glitch] Minor parsing issue with JSON output. Entering fallback... ")
                        try:
                           result = ast.literal_eval(clean_text)
                           parsed_list = result.get("translations", [])
                        except Exception:
                           raise Exception(f"Model generated a broken snippet (JSON: '{json_err}').")
                
                if len(parsed_list) != len(texts):
                    raise Exception(f"Uneven batch size. Expected {len(texts)}, got {len(parsed_list)}.")
                    
                return parsed_list
                
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg or "resource" in error_msg:
                    wait_time = 5
                    self.log(f"[Limit] API overloaded. Resting 5s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                elif "prohibited" in error_msg or "blocked" in error_msg or "safety" in error_msg or "none" in error_msg:
                    self.log(f"[Blocked] Google policy strictly blocked this scene's content. Skipping batch.")
                    return texts
                else:
                    self.log(f"[Crash / Retry] {e} (Attempt {attempt + 1}/{max_retries})")

        self.log("[WARNING] Batch failed entirely. Entering 1-by-1 fallback mode...")
        fallback_list = []
        for single_text in texts:
            try:
                # 1-by-1 safe generation
                self.log("Translating single line to rescue skipping...")
                fallback_prompt = json.dumps([single_text], ensure_ascii=False)
                res = core_client.models.generate_content(
                    model=model_name,
                    contents=fallback_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.3,
                        safety_settings=safety_settings
                    )
                )
                res_dict = json.loads(re.sub(r'```(?:json)?|```', '', res.text).strip())
                fallback_list.append(res_dict.get("translations", [single_text])[0])
                time.sleep(1) # prevent hitting rate limits
            except Exception as e:
                self.log(f"Single fallback failed. Keeping original text.")
                fallback_list.append(single_text)
                
        return fallback_list


    def run_translator_logic(self, api_key, target_lang):
        try:
            client = genai.Client(api_key=api_key)
            model_selected = self.model_var.get()
            batch_size = 40
            
            base, ext = os.path.splitext(self.file_path)
            lang_code = target_lang[:2].upper() # Polish -> PO, English -> EN etc. for filename
            output_file = f"{base}_{lang_code}{ext}"
            progress_file = f"{base}_progress.json"
            
            start_index = 0
            if os.path.exists(output_file) and os.path.exists(progress_file):
                try:
                     with open(progress_file, 'r', encoding='utf-8') as f:
                         start_index = json.load(f).get("last_index", 0)
                     self.log(f"🔄 Restored previously halted progress (Batch {start_index // batch_size + 1})")
                     with open(output_file, 'r', encoding='utf-8') as f:
                         subtitles = list(srt.parse(f.read()))
                except Exception:
                    self.log("[Resume Error] Starting from scratch.")
                    start_index = 0
                    
            if start_index == 0:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    subtitles = list(srt.parse(f.read()))
                self.log(f"✅ File analyzed. Found {len(subtitles)} dialogue lines. Working...")

            total_subs = len(subtitles)

            for i in range(start_index, total_subs, batch_size):
                batch_subs = subtitles[i:i + batch_size]
                batch_texts = [sub.content for sub in batch_subs]
                
                try:
                    translated_texts = self.translate_batch(client, model_selected, batch_texts, target_lang)
                except Exception as ex:
                    self.log(f"\n[CRITICAL FAILURE] Process forcefully stopped: {ex}\nSaved state can be resumed later.")
                    break 
                     
                if len(translated_texts) == len(batch_texts):
                    for j, translated_text in enumerate(translated_texts):
                        subtitles[i + j].content = translated_text
                else:
                    self.log(f"\n[Warning] Uneven batch result. Original text skipped.")
                    
                with open(output_file, 'w', encoding='utf-8') as f:
                   f.write(srt.compose(subtitles))
                   
                with open(progress_file, 'w', encoding='utf-8') as pf:
                    json.dump({"last_index": i + batch_size}, pf)
                    
                current_progress = min(1.0, (i + batch_size) / total_subs)
                percent = int(current_progress * 100)
                
                self.after(0, lambda p=current_progress, perc=percent: self.update_progress(p, perc))

            if os.path.exists(progress_file):
                os.remove(progress_file)
                
            self.log(f"\n🎉 DONE!\nOutput file saved next to original as: {os.path.basename(output_file)}")
            self.after(0, self.finish_translation)
            
        except Exception as god_error:
            self.log(f"GENERAL DISASTER: {god_error}")
            self.after(0, self.finish_translation)

    def update_progress(self, current_progress, percent):
         self.progress_bar.set(current_progress)
         self.progress_label.configure(text=f"Progress: {percent}%")

    def finish_translation(self):
         self.is_translating = False
         self.start_btn.configure(state="normal", text="START TRANSLATION", fg_color=["#3B8ED0", "#1F6AA5"])
         self.file_btn.configure(state="normal")

if __name__ == "__main__":
    app = TranslatorGUI()
    app.mainloop()
