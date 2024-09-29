from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict
import requests
import datetime
import shutil
import math
import json
import time
import os

PATH_TEMP_ITEM = "../data/img/temp_item" # Путь для предметов магазина (temp)
PATH_COLLAGE = "../data/img/collage.jpg" # Путь для сохранения коллажа

# Обработка полученных данных с Fortnite API
def load_info(data_local: Dict) -> List[List[str]]:
    all_info = []
    # Перебор элементов в data -> entries, все предметы магазина
    for entries in data_local["data"]["entries"]:
        try:
            price = entries["finalPrice"]
            name = entries["bundle"]["name"]
            image = entries["bundle"]["image"]

            info = [price, name, image]
            all_info.append(info)
        except KeyError:
            if "newDisplayAsset" in entries:
                new_display_asset = entries["newDisplayAsset"]
                if "materialInstances" in new_display_asset:
                    material_instances = new_display_asset["materialInstances"]
                    if len(material_instances) > 0:
                        if "brItems" in entries:
                            name = entries["brItems"][0]["name"]
                        else:
                            continue

                        price = entries["finalPrice"]
                        image = material_instances[0]["images"]["Background"]

                        info = [price, name, image]
                        all_info.append(info)
    return all_info


# Загрузка картинок полученных с Fortnite API
def load_img(list_item: List[List[str]]) -> None:
    if not os.path.isdir(PATH_TEMP_ITEM):
        os.mkdir(PATH_TEMP_ITEM)

    count = len(list_item) + 1
    for item in list_item:
        img_data = requests.get(item[2]).content
        with open(f'{PATH_TEMP_ITEM}/{item[1]}.jpg', 'wb') as handler:
            handler.write(img_data)
            count -= 1
            print("Download image...", f"{count} left.")

    print("Download done!")


# Оптимальное соотношение rows & cols (1:1)
def find_optimal_dimensions(num_images: int) -> List[int]:
    square_root = math.sqrt(num_images)
    if float(int(square_root)) < square_root:
        return [int(square_root) + 1, int(square_root) + 1]
    else:
        return [int(square_root), int(square_root)]


# Создание коллажа из загруженных картинок
def create_collage(image_paths: List[str], text_list: List[str] = None) -> None:
    rows, cols = find_optimal_dimensions(len(image_paths))

    # Открытие первого изображения для определения размера
    first_image = Image.open(image_paths[0])
    width, height = first_image.size
    first_image.close()  # Закрытие изображения

    # Определение размера каждого изображения в коллаже
    grid_width = width * cols
    grid_height = height * rows

    # Создание нового изображения для коллажа
    collage = Image.new("RGB", (grid_width, grid_height))

    # Создание черной полоски
    strip_height = 150  # Высота полоски
    strip = Image.new("RGB", (grid_width, strip_height), color="black")
    draw = ImageDraw.Draw(strip)

    # Написание текста на полоске
    font = ImageFont.truetype("arial.ttf", 100)  # Выберите шрифт и размер
    text = f"{datetime.datetime.now().strftime('%d-%m-%Y')}"  # Текст для полоски
    text_width, text_height = font.getbbox(text)[2] - font.getbbox(text)[0], font.getbbox(text)[3] - font.getbbox(text)[1]
    text_x = (grid_width - text_width) // 2  # Центрирование текста
    text_y = (strip_height - text_height) // 2  # Центрирование текста по высоте
    draw.text((text_x, text_y), text, font=font, fill="white", align="center")

    # Вставка полоски в коллаж
    collage.paste(strip, (0, 0))

    # Отступ для черной полоски сверху
    y_offset = 150
    # Добавление изображений в коллаж
    for i, image_path in enumerate(image_paths):
        row = i // cols  # Номер строки
        col = i % cols  # Номер столбца
        x = col * width
        y = row * height + y_offset
        image = Image.open(image_path)

        # Добавление текста для картинок в коллаже
        if text_list is not None:
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("arial.ttf", 70)  # Выберите шрифт и размер
            text = text_list[i]

            text_lines = text.split(", ")
            line1 = " ".join(text_lines[:len(text_lines) // 2])
            line2 = " ".join(text_lines[len(text_lines) // 2:])

            bbox1 = font.getbbox(line1)
            bbox2 = font.getbbox(line2)
            text_width1 = bbox1[2] - bbox1[0]
            text_width2 = bbox2[2] - bbox2[0]
            text_height1 = bbox1[3] - bbox1[1]
            text_height2 = bbox2[3] - bbox2[1]
            text_x1 = (width - text_width1) // 2  # Центрирование первой строки
            text_x2 = (width - text_width2) // 2  # Центрирование второй строки
            text_y1 = height - text_height1 - text_height2 - 800  # Позиционирование первой строки
            text_y2 = text_y1 + text_height1 + 5 # Позиционирование второй строки

            draw.text((text_x1, text_y1), line1, font=font, fill="black", stroke_width=2, stroke_fill="black", align="center")
            draw.text((text_x2, text_y2), line2, font=font, fill="black", stroke_width=2, stroke_fill="black", align="center")

            draw.text((text_x1, text_y1), line1, font=font, fill="white", align="center")
            draw.text((text_x2, text_y2), line2, font=font, fill="white", align="center")

        collage.paste(image, (x, y))
        image.close()

    # Сохранение коллажа
    collage.save(PATH_COLLAGE)
    resized_image = collage.resize((collage.width // 2, collage.height // 2)) # Уменьшение размера
    resized_image.save(PATH_COLLAGE)
    print("Collage created.")

    # Удаление картинок из items
    shutil.rmtree(PATH_TEMP_ITEM)
    print("All picture delete.\n")


# Получение данных из Fortnite API
def get_request() -> None:
    response = requests.get("https://fortnite-api.com/v2/shop", params={"language": "ru"})
    data = json.loads(response.text)

    if data["status"] == 200:
        list_item = load_info(data)
        print("Request done!")
        load_img(list_item)

        # Создания коллажа
        text_l = []
        path_l = []
        for i in range(len(list_item)):
            text_l.append(f"{list_item[i][1]}, {list_item[i][0]}VB")
            path_l.append(f"{PATH_TEMP_ITEM}/{list_item[i][1]}.jpg")
        create_collage(path_l, text_l)
    else:
        print(data["status"])
        print(data["error"])

        # При ошибке повторяем запрос
        print("Try request again...")
        time.sleep(1)
        get_request()


# Запуск скрипта
def start_update() -> None:
    get_request()