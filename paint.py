import logging
import time
import random

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import logger_setup

from coordinate import convert_coords_from_pixel_to_canvas, moove_template
from colors import color_from_template, color_from_screen
from claim import get_balance
from templates import templates, tournament_templates
from config import real_colors, pupmkin_colors, t_size

from test import get_top_colors

def get_energy(driver):
    try:
        energy_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'placeholder')]"
        )
        energy = int(
            energy_element.get_attribute("innerHTML")
            .split("<span")[2][1:]
            .replace("</span>", "")
        )
        return energy
    except Exception:
        raise

def get_template(driver):
    try:
        template_element = driver.find_element(
            By.XPATH, "//img[contains(@src, 'template')]"
        )
        template_key = (
            template_element.get_attribute("src").split("templates/")[1].split(".png")[0]
        )
        template = templates[template_key]
        return template
    except Exception as e:
        logging.error(f"Error in get_template: {e}")
        raise

def change_color(color, canvas, driver):
    try:
        active_color_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'active_color')]"
        )
        active_color = tuple(
            map(
                int,
                active_color_element.get_attribute("style")
                .replace("background-color: rgb(", "")[:-2]
                .split(", "),
            )
        )

        if active_color == color:
            return True
        else:
            active_color_element.click()
            opacity = "0"
            while opacity != "1":
                panel = driver.find_element(
                    By.XPATH, "//div[contains(@class, 'expandable_panel_layout')]"
                )
                opacity = panel.get_attribute("style").split(" ")[-1][:-1]
            need_color = driver.find_element(
                By.XPATH, f"//div[contains(@style, '{color}')]"
            )
            need_color.click()
            time.sleep(0.5)
            active_color_element.click()
            time.sleep(1)
            return True

    except ElementClickInterceptedException:
        return False

    except Exception as e:
        logging.error(f"Error in change_color: {e}")
        raise

def check_tanos(driver, canvas, direction, tanos):
    try:
        if (datetime.now() - tanos["time"]).seconds < 7:
            time.sleep(random.uniform(9.0, 11.0))

            template_btn = driver.find_element(
                By.XPATH, "//div[contains(@class, 'buttons_container')]/button/img"
            )
            time.sleep(0.5)
            template_btn.click()
            time.sleep(2)
            template_btn.click()
            time.sleep(1)

            offset = direction
            actions = ActionChains(driver)

            # Зажимаем ЛКМ, перемещаем элемент и отпускаем
            actions.click_and_hold(canvas).move_by_offset(offset[0], offset[1]).release().perform()
            time.sleep(2)

            logging.info("TANOS was dodged")
            return True
        else:
            return False
        
    except Exception as e:
        logging.error(f"Error in check_tanos: {e}")
        raise

def check_tanos_long(driver, canvas, direction):
    try:
        alarm = driver.find_element(By.XPATH, "//*[contains(text(), 'I AM')]")
        time.sleep(random.uniform(9.0, 11.0))

        template_btn = driver.find_element(
            By.XPATH, "//div[contains(@class, 'buttons_container')]/button/img"
        )
        time.sleep(0.5)
        template_btn.click()
        time.sleep(2)
        template_btn.click()
        time.sleep(1)

        offset = direction
        moove_template(driver, canvas, offset)

        logging.info("TANOS was dodged")
        return True
    
    except NoSuchElementException:
        return False
        
    except Exception as e:
        logging.error(f"Error in check_tanos: {e}")
        raise

def enable_speed(driver):
        try:
            driver.implicitly_wait(3)
            speed = driver.find_elements(
                By.XPATH, "//button[contains(@class, 'shop_button')]"
            )[3]
            speed.click()
            close = driver.find_element(By.XPATH, "//div[contains(@class, 'header')]/div[contains(@class, 'close')]")
            time.sleep(2)
            close.click()
            driver.implicitly_wait(0)
        except NoSuchElementException:
            driver.implicitly_wait(0)
        except Exception:
            raise

def enable_fast_mode(driver):
    try:
        fast_btn = driver.find_elements(
            By.XPATH, "//button[contains(@class, 'shop_button')]"
        )[4]
        fast_btn_class = fast_btn.get_attribute("class")
        if "fast_mode_button_enabled" in fast_btn_class:
            return True
        fast_btn.click()
        time.sleep(0.5)
        check_fast_btn = driver.find_element(
            By.XPATH, "//button[contains(@class, 'fast_mode_button_enabled')]"
        )
        return True
    except ElementClickInterceptedException:
        return False
    except Exception:
        logging.error("Error in enable_fast_mode")
        raise

def get_start(canvas, driver, profiles, profile_id):
    try:
        canvas.click()
        time.sleep(0.2)
        element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'pixel_info_text')]"
        )
        text = element.get_attribute("innerHTML")
        coords = text[: text.find("&")]
        x_pixel, y_pixel = coords.split(", ")
        x, y = int(x_pixel), int(y_pixel)
        start_x = x - x % t_size
        start_y = y - y % t_size
        start = [start_x, start_y]
        profiles[profile_id]["start"] = start
        return start
    except ElementClickInterceptedException:
        if check_tanos_long(driver, canvas, profiles[profile_id]["direction"]):
            return get_start(canvas, driver, profiles, profile_id)
        else:
            raise
    
    except Exception:
        raise

def get_other_colors(profiles, template_path, direction):
    picked_colors = [profile["color"] for profile in profiles.values() if "temp" in profile and profile["temp"] == template_path and "direction" in profile and profile["direction"] == direction and "color" in profile]
    return picked_colors

def check_colibration(driver, real_canvas_x, real_canvas_y, x_canvas_zero, y_canvas_zero, x_pixel_zero, y_pixel_zero, ratio_x, ratio_y):
    element = driver.find_element(
        By.XPATH, "//div[contains(@class, 'pixel_info_text')]"
    )
    text = element.get_attribute("innerHTML")
    coords = text[: text.find("&")]
    x_pixel, y_pixel = map(int, coords.split(", "))
    expected_x, expected_y = convert_coords_from_pixel_to_canvas(
        x_pixel, y_pixel, x_canvas_zero, y_canvas_zero, x_pixel_zero, y_pixel_zero, ratio_x, ratio_y
    )
    print(expected_x, expected_y)
    print(real_canvas_x, real_canvas_y)
    return real_canvas_x == expected_x and real_canvas_y == expected_y

def start_paint(
    x_canvas_zero,
    y_canvas_zero,
    x_pixel_zero,
    y_pixel_zero,
    x_pixel_end,
    y_pixel_end,
    ratio_x,
    ratio_y,
    driver,
    canvas,
    profile_id,
    profiles,
    tanos,
):
    profile_name = profiles[profile_id]["name"]
    try:
        start_balance = get_balance(driver)
        # template = get_template(driver)
        template_path = profiles[profile_id]["temp"]
        if "start" in profiles[profile_id]:
            start = profiles[profile_id]["start"]
        else:
            start = get_start(canvas, driver, profiles, profile_id)
        energy = get_energy(driver)
        colored = 0
        pixel_coords = [[(x, y) for x in range(max(x_pixel_zero, start[0]), min(x_pixel_end, start[0] + t_size - 1) + 1)] for y in range(max(y_pixel_zero, start[1]), min(y_pixel_end, start[1] + t_size - 1) + 1)]
        template_colors, opacity = color_from_template(template_path, pixel_coords, start)
        canvas_coords = [
            [
                convert_coords_from_pixel_to_canvas(
                    coord[0],
                    coord[1],
                    x_canvas_zero,
                    y_canvas_zero,
                    x_pixel_zero,
                    y_pixel_zero,
                    ratio_x,
                    ratio_y,
                ) for coord in row
            ] for row in pixel_coords
        ]

        range_x = x_pixel_end - x_pixel_zero + 1
        range_y = y_pixel_end - y_pixel_zero + 1
        
        top_colors = get_top_colors(template_path, template_colors, opacity)
        top_color = random.choice(top_colors)
        direction = profiles[profile_id]["direction"][:]
        if not change_color(top_color, canvas, driver):
            if check_tanos_long(driver, canvas, direction):
                start_paint(
                    x_canvas_zero,
                    y_canvas_zero,
                    x_pixel_zero,
                    y_pixel_zero,
                    x_pixel_end,
                    y_pixel_end,
                    ratio_x,
                    ratio_y,
                    driver,
                    canvas,
                    profile_id,
                    profiles,
                    tanos,
                )
                return
            else:
                logging.error(f"Profile {profiles[profile_id]["name"]}. Error while changing color without tanos")
                return
        time.sleep(0.5)
        if not enable_fast_mode(driver):
            if check_tanos_long(driver, canvas, direction):
                start_paint(
                    x_canvas_zero,
                    y_canvas_zero,
                    x_pixel_zero,
                    y_pixel_zero,
                    x_pixel_end,
                    y_pixel_end,
                    ratio_x,
                    ratio_y,
                    driver,
                    canvas,
                    profile_id,
                    profiles,
                    tanos,
                )
                return
            else:
                logging.error(f"Profile {profiles[profile_id]["name"]}. Error while enabling fast mode without tanos")
                return
        
        # if int(profiles[profile_id]["name"]) in [14]:
        #     enable_speed(driver)
        driver.implicitly_wait(0)

        # if (datetime.now() - tanos["time"]).seconds < 150:
        #     allowed_colors = real_colors + pupmkin_colors
        # else:
        #     allowed_colors = pupmkin_colors
        allowed_colors = real_colors + pupmkin_colors
        while energy != 0:
            # start_time = time.time()
            screen_colors = color_from_screen(canvas_coords, canvas)
            # time_screen = time.time() - start_time
            # start_time = time.time()
            if opacity == 0:
                indexes = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in allowed_colors]
                indexes1 = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] != top_color and screen_colors[i][j] in allowed_colors]
            else:
                indexes = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] == top_color and screen_colors[i][j] in allowed_colors and opacity[i][j] == 255]
                indexes1 = [(i, j) for i in range(range_y) for j in range(range_x) if template_colors[i][j] != screen_colors[i][j] and template_colors[i][j] != top_color and screen_colors[i][j] in allowed_colors and opacity[i][j] == 255]
            if len(indexes) == 0 and len(indexes1) == 0:
                if check_tanos_long(driver, canvas, direction):
                    start_paint(
                        x_canvas_zero,
                        y_canvas_zero,
                        x_pixel_zero,
                        y_pixel_zero,
                        x_pixel_end,
                        y_pixel_end,
                        ratio_x,
                        ratio_y,
                        driver,
                        canvas,
                        profile_id,
                        profiles,
                        tanos,
                    )
                    return
                continue
            elif len(indexes) == 0 and len(indexes1) != 0:
                i, j = random.choice(indexes1)
                new_color = template_colors[i][j]
                if not change_color(new_color, canvas, driver):
                    if check_tanos_long(driver, canvas, direction):
                        start_paint(
                            x_canvas_zero,
                            y_canvas_zero,
                            x_pixel_zero,
                            y_pixel_zero,
                            x_pixel_end,
                            y_pixel_end,
                            ratio_x,
                            ratio_y,
                            driver,
                            canvas,
                            profile_id,
                            profiles,
                            tanos,
                        )
                        return
                    else:
                        continue
                top_color = new_color
                if check_tanos_long(driver, canvas, direction):
                    start_paint(
                        x_canvas_zero,
                        y_canvas_zero,
                        x_pixel_zero,
                        y_pixel_zero,
                        x_pixel_end,
                        y_pixel_end,
                        ratio_x,
                        ratio_y,
                        driver,
                        canvas,
                        profile_id,
                        profiles,
                        tanos,
                    )
                    return
                continue

            i, j = random.choice(indexes)
            canvas_x, canvas_y = canvas_coords[i][j][0], canvas_coords[i][j][1]

            # time_find = time.time() - start_time
            
            miss = not bool(random.randint(0, 70))
            if miss:
                if len(top_colors) > 1:
                    repaint_color = [i for i in top_colors if i != top_color][0]
                else:
                    real_colors_except_template = [i for i in real_colors if i != top_color]
                    repaint_color = random.choice(real_colors_except_template)

                if not change_color(repaint_color, canvas, driver):
                    if check_tanos_long(driver, canvas, direction):
                        start_paint(
                            x_canvas_zero,
                            y_canvas_zero,
                            x_pixel_zero,
                            y_pixel_zero,
                            x_pixel_end,
                            y_pixel_end,
                            ratio_x,
                            ratio_y,
                            driver,
                            canvas,
                            profile_id,
                            profiles,
                            tanos,
                        )
                        return
                    else:
                        continue
                time.sleep(0.5)
                if not paint(canvas_x, canvas_y, driver, canvas, direction):
                    if check_tanos_long(driver, canvas, direction):
                        start_paint(
                            x_canvas_zero,
                            y_canvas_zero,
                            x_pixel_zero,
                            y_pixel_zero,
                            x_pixel_end,
                            y_pixel_end,
                            ratio_x,
                            ratio_y,
                            driver,
                            canvas,
                            profile_id,
                            profiles,
                            tanos,
                        )
                        return
                    else:
                        top_color = repaint_color
                        continue
                if not change_color(top_color, canvas, driver):
                    if check_tanos_long(driver, canvas, direction):
                        start_paint(
                            x_canvas_zero,
                            y_canvas_zero,
                            x_pixel_zero,
                            y_pixel_zero,
                            x_pixel_end,
                            y_pixel_end,
                            ratio_x,
                            ratio_y,
                            driver,
                            canvas,
                            profile_id,
                            profiles,
                            tanos,
                        )
                        return
                    else:
                        top_color = repaint_color
                        continue
                logging.info(f"Profile {profile_name}. Miss dropped")
            
            else:
                # start_time = time.time()
                if not paint(canvas_x, canvas_y, driver, canvas, direction):
                    if check_tanos_long(driver, canvas, direction):
                        start_paint(
                            x_canvas_zero,
                            y_canvas_zero,
                            x_pixel_zero,
                            y_pixel_zero,
                            x_pixel_end,
                            y_pixel_end,
                            ratio_x,
                            ratio_y,
                            driver,
                            canvas,
                            profile_id,
                            profiles,
                            tanos,
                        )
                        return
                    else:
                        continue
                # time_paint = time.time() - start_time

            # print(time_screen, time_find, time_paint)
            colored += 1
            time.sleep(random.uniform(0.5, 1.5))
            energy = get_energy(driver)
            # if int(profiles[profile_id]["name"]) in [14] and energy == 0:
            #     energy = 25
            if check_tanos_long(driver, canvas, direction):
                start_paint(
                    x_canvas_zero,
                    y_canvas_zero,
                    x_pixel_zero,
                    y_pixel_zero,
                    x_pixel_end,
                    y_pixel_end,
                    ratio_x,
                    ratio_y,
                    driver,
                    canvas,
                    profile_id,
                    profiles,
                    tanos,
                )
                return
        time.sleep(2)
        end_balance = get_balance(driver)
        profit = end_balance - start_balance

        profiles[profile_id]["balance"] = end_balance
        profiles[profile_id]["last_paint"] = datetime.now()
        profiles[profile_id]["last_profit"] = profit
        driver.implicitly_wait(10)
        logging.info(
            f"Profile {profile_name}. Painting completed. Pixels colored: {colored}, Profit: {profit}, Balance: {end_balance}"
        )
            
        return

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in start_paint: {e}")
        raise


def paint(x, y, driver, canvas, direction):
    try:
        ActionChains(driver).move_to_element_with_offset(canvas, x, y).click().perform()
        return True

    except ElementClickInterceptedException:
        return False

    except Exception as e:
        logging.error(f"Error in paint: {e}")
        raise
