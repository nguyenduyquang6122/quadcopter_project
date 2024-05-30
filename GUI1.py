import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time
from datetime import datetime
from tkinter import filedialog
from tkinter import messagebox


# Open the video file
start_time = time.time()

class CameraApp:
    def __init__(self, root, camera_index=0):
        self.root = root
        self.CamerasID = 0
        self.cap = cv2.VideoCapture(self.CamerasID)
        self.root.title("ICD-FPV Camera")

        self.file_path = None

        self.is_recording = False
        self.video_writer = None
        self.record_start_time = None
        
        self.w_size = (710, 650)

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        # Tạo thanh menu
        menu_bar = tk.Menu(root)

        # Tạo menu Edit
        edit_menu = tk.Menu(menu_bar, tearoff=0)

        # Tạo menu con cho "Config Camera ID"
        config_camera_menu = tk.Menu(edit_menu, tearoff=0)
        config_camera_menu.add_command(label="ID1", command=self.config_camera_id_1)
        config_camera_menu.add_command(label="ID2", command=self.config_camera_id_2)

        # Thêm menu con vào "Config Camera ID"
        edit_menu.add_cascade(label="Config Camera ID", menu=config_camera_menu)

        # Thêm menu Edit vào menu bar
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Tạo menu Help
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About us", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Thiết lập thanh menu cho cửa sổ chính
        root.config(menu=menu_bar)

        self.capture_button = tk.Button(root, text="Capture Photo", command=self.capture_photo)
        self.capture_button.place(x=310, y=600, width=100, height=30)

        self.record_button = tk.Button(root, text="Record Video", command=self.toggle_record)
        self.record_button.place(x=210, y=600, width=100, height=30)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.exit_button.place(x=410, y=600, width=100, height=30)

        self.root.after(1000, self.update)


    def update(self):
        global start_time
        current_time = time.time()

        self.ret, self.frame = self.cap.read()
        if self.ret == False:
            self.config_camera_id_1()
            messagebox.showerror('ID Error', 'Error: This Camera ID does not exist!')

        video_width = self.frame.shape[0]
        video_height = self.frame.shape[1]
        video_scale = video_height/video_width
        
        # print(self.ret)
        # print(self.frame)

        if self.ret:
            
            window_size = root.geometry()

            # Tách chuỗi theo ký tự 'x' để lấy chiều rộng
            # và sau đó tìm vị trí của dấu '+' để chỉ lấy phần tử đầu tiên
            width, rest = window_size.split('x')
            height = rest.split('+')[0]

            # Chuyển đổi chuỗi sang số nguyên
            width = int(width)
            height = int(height)

            if self.w_size != (width, height):
                self.capture_button.destroy()
                self.record_button.destroy()
                self.exit_button.destroy()

                self.capture_button = tk.Button(root, text="Capture Photo", command=self.capture_photo)
                self.capture_button.place(x=int(width/2 - 30), y=int(height-40), width=100, height=30)

                self.record_button = tk.Button(root, text="Record Video", command=self.toggle_record)
                self.record_button.place(x=int(width/2 - 130), y=int(height-40), width=100, height=30)

                self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
                self.exit_button.place(x=int(width/2 + 70), y=int(height-40), width=100, height=30)

            self.w_size = (width, height)

            w = height*video_scale

            dim = (int(w), height)

            resized = cv2.resize(self.frame, dim, interpolation=cv2.INTER_AREA)

            if current_time - start_time >= 0:
                start_time = time.time()
            else:
                resized = resized

            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

            img = ImageTk.PhotoImage(Image.fromarray(rgb_image))

            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

            if self.is_recording:
                if self.file_path is not None:
                    if self.video_writer is None:
                        fourcc = cv2.VideoWriter_fourcc(*"XVID")
                        width, height = self.frame.shape[1], self.frame.shape[0]
                        self.video_path = self.file_path + "/" + datetime.now().strftime("%H_%M_%S_%M_%d_%m_%Y") + ".avi"
                        self.video_writer = cv2.VideoWriter(self.video_path, fourcc, 20.0, (width, height))
                        self.record_start_time = time.time()

                # elapsed_time = time.time() - self.record_start_time
                # formatted_elapsed_time = time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time))
                # self.record_time_label.config(text=formatted_elapsed_time)

                    self.video_writer.write(self.frame)
        self.root.after(10, self.update)
    
    def config_camera_id_1(self):
        self.CamerasID = 0
        try:
            self.cap = cv2.VideoCapture(self.CamerasID)
            self.ret, self.frame = self.cap.read()
            if self.ret is False:
                self.CamerasID = 1
                self.cap = cv2.VideoCapture(self.CamerasID)
                self.ret, self.frame = self.cap.read()
                messagebox.showerror('ID Error', 'Error: This Camera ID does not exist!')
        except Exception as e:
            messagebox.showerror('ID Error', 'Error: This Camera ID does not exist!')

    def config_camera_id_2(self):
        self.CamerasID = 1
        try:
            self.cap = cv2.VideoCapture(self.CamerasID)
            self.ret, self.frame = self.cap.read()
            if self.ret is False:
                self.CamerasID = 0
                self.cap = cv2.VideoCapture(self.CamerasID)
                self.ret, self.frame = self.cap.read()
                messagebox.showerror('ID Error', 'Error: This Camera ID does not exist!')

        except Exception as e:
            messagebox.showerror('ID Error', 'Error: This Camera ID does not exist!')

    def ChoosecameraID(self):
        pass
    
    def about(self):
        new_window = tk.Toplevel(root)
        new_window.title("About us")

        label = tk.Label(new_window, text="Nhóm Drone xin chào người dùng! \n "
                                          "Nhóm gồm những thành viên sau: \n"
                                          "Nguyễn Quang Huy \n"
                                          "Nguyễn Duy Quang \n"
                                          "Chử Tiến Duy \n"
                                          )
        label.pack(padx=20, pady=20)

    def capture_photo(self):
        if self.file_path is None:
            self.file_path = filedialog.askdirectory()
        self.path_pic = self.file_path + "/" + datetime.now().strftime("%H_%M_%S_%M_%d_%m_%Y") + "_photo.jpg"
        cv2.imwrite(self.path_pic, self.frame)
        print("Photo captured!")

    def toggle_record(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            if self.file_path is None:
                self.file_path = filedialog.askdirectory()
            self.record_button.config(text="Stop Record")
            print("Recording started.")
        else:
            if self.video_writer is not None:
                self.video_writer.release()
                self.record_button.config(text="Record Video")
                print("Recording stopped.")
            self.video_writer = None

    def exit_app(self):
        if self.cap is not None:
            self.cap.release()
        if self.is_recording:
            self.toggle_record()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("710x650")
    app = CameraApp(root)
    root.mainloop()