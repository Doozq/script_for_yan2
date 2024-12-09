from templates import tournament_templates
from PIL import Image
from config import t_size


# for template_path in tournament_templates:
#     path = "templates\\" + template_path
#     image = Image.open(path)
#     opacity = len(image.getpixel((0, 0))) == 4
#     colors = {}
#     for y in range(64):
#         for x in range(64):
#             pixel = image.getpixel((x, y))
#             if opacity:
#                 if pixel[3] != 255:
#                     continue
#                 else:
#                     pixel = pixel[:3]

#             colors[pixel] = colors.get(pixel, 0) + 1
#     # Сортируем элементы словаря по значениям в порядке убывания
#     sorted_items = sorted(colors.items(), key=lambda item: item[1], reverse=True)

#     # Берем два первых элемента (наибольшие значения)
#     top = [key for key, value in sorted_items[:2]]

#     tournament_templates[template_path]["top_colors"] = top

# print(tournament_templates)


def get_top_colors(template_path, template_colors, opacity):
    colors = {}
    for i in range (len(template_colors)):
        for j in range(len(template_colors[i])):
            color = template_colors[i][j]
            if opacity != 0:
                if opacity[i][j] != 255:
                    continue

            colors[color] = colors.get(color, 0) + 1
    # Сортируем элементы словаря по значениям в порядке убывания
    sorted_items = sorted(colors.items(), key=lambda item: item[1], reverse=True)

    # Берем два первых элемента (наибольшие значения)
    top = [key for key, value in sorted_items[:2]]

    return top