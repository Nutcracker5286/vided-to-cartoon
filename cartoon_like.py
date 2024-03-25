import cv2 as cv
import numpy as np

def cartoonize_image(img, ds_factor=4, sketch_mode=False):
    # 이미지를 다운샘플링합니다.
    img_small = cv.resize(img, None, fx=1.0/ds_factor, fy=1.0/ds_factor, interpolation=cv.INTER_AREA)

    # 색상을 단순화합니다.
    num_repetitions = 10
    sigma_color = 5
    sigma_space = 7
    size = 5

    # Bilateral Filter를 적용합니다.
    temp = cv.bilateralFilter(img_small, size, sigma_color, sigma_space)
    img_small = cv.bilateralFilter(temp, size, sigma_color, sigma_space)
    img_small = cv.bilateralFilter(img_small, size, sigma_color, sigma_space)
    img_small = cv.bilateralFilter(img_small, size, sigma_color, sigma_space)

    # 원본 이미지로 업샘플링합니다.
    img_output = cv.resize(img_small, None, fx=ds_factor, fy=ds_factor, interpolation=cv.INTER_LINEAR)

    # 그레이스케일로 변환하고 중간 톤을 제거합니다.
    gray = cv.cvtColor(img_output, cv.COLOR_BGR2GRAY)
    blur = cv.medianBlur(gray, 13)
    img_sketch = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 9, 2)

    # 스케치 모드인 경우 스케치 이미지를 반환합니다.
    if sketch_mode:
        return cv.cvtColor(img_sketch, cv.COLOR_GRAY2BGR)

    # 스케치 이미지와 색상 이미지를 결합합니다.
    img_sketch = cv.cvtColor(img_sketch, cv.COLOR_GRAY2BGR)
    img_cartoon = cv.bitwise_and(img_output, img_sketch)

    return img_cartoon
if __name__ == '__main__':
    video_name='data/'+input('원하는 비디오 파일 이름, 형식을 입력하시오: ')
    video=cv.VideoCapture(video_name)
    assert video.isOpened(), '비디오 파일을 열 수 없습니다.'+video_name

    # fps 및 wait time
    fps= video.get(cv.CAP_PROP_FPS)
    wait_msec=int(1/fps*1000)
    target=cv.VideoWriter()
    target_fourcc='XVID'

    while True:
        valid, img = video.read()
        if not valid:
            break
        frame = int(video.get(cv.CAP_PROP_POS_FRAMES))

        # 영상을 만듭니다
        if not target.isOpened():
            h,w,*_=img.shape
            is_color = (img.ndim > 2) and (img.shape[2] > 1)
            cv.destroyAllWindows()
            target.open('output.avi', cv.VideoWriter_fourcc(*target_fourcc), fps, (w, h), is_color)


        # img를 카툰화합니다.
        output_image = cartoonize_image(img, ds_factor=4, sketch_mode=False)
        
        # 이미지를 띄움니다
        cv.imshow('Cartoonized Image', output_image)
        key=cv.waitKey(wait_msec)
        if key == 27: # ESC
            cv.destroyAllWindows() 
            break
        if key == ord(' '):
            key=cv.waitKey() 

        # 비디오를 저장합니다.
        target.write(output_image)
    target.release()
    video.release()
    cv.destroyAllWindows() 