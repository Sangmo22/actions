import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def test_notes_can_be_created():
    # Arrange
    driver = webdriver.Chrome()
    driver.get('http://127.0.0.1:8000/notes/add/')

    # Act
    driver.find_element(By.NAME, 'title').send_keys('Django Course')
    driver.find_element(By.NAME, 'description').send_keys(
        'Complete course with urls, templates, models, etc')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(2)  # Bad but easy

    # Assert
    title = driver.find_element(By.TAG_NAME, 'td').text
    assert 'Django Course' in title

    driver.quit()


def test_error_occurs_if_description_is_less_than_10_chars_long():
    # Arrange
    driver = webdriver.Chrome()
    driver.get('http://127.0.0.1:8000/notes/add/')

    # Act
    driver.find_element(By.NAME, 'title').send_keys('Django Course')
    driver.find_element(By.NAME, 'description').send_keys('dj')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(2)  # Bad but easy

    # Assert
    error = driver.find_element(By.TAG_NAME, 'li').text
    assert 'Description must be at least 10 characters long' in error

    driver.quit()