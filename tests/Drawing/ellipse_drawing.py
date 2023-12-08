# Ellipse Drawing
#
# This example shows off drawing ellipses on the CanMV Cam.

from media.camera import *
from media.display import *
from media.media import *
import time, os, gc, urandom

DISPLAY_WIDTH = ALIGN_UP(1920, 16)
DISPLAY_HEIGHT = 1080

def camera_init():
    # use hdmi for display
    display.init(LT9611_1920X1080_30FPS)
    # config vb for osd layer
    config = k_vb_config()
    config.max_pool_cnt = 1
    config.comm_pool[0].blk_size = 4*DISPLAY_WIDTH*DISPLAY_HEIGHT
    config.comm_pool[0].blk_cnt = 1
    config.comm_pool[0].mode = VB_REMAP_MODE_NOCACHE
    # meida buffer config
    ret = media.buffer_config(config)
    # init default sensor
    camera.sensor_init(CAM_DEV_ID_0, CAM_DEFAULT_SENSOR)
    # set chn0 output size
    camera.set_outsize(CAM_DEV_ID_0, CAM_CHN_ID_0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    # set chn0 output format
    camera.set_outfmt(CAM_DEV_ID_0, CAM_CHN_ID_0, PIXEL_FORMAT_YUV_SEMIPLANAR_420)
    # create meida source device
    globals()["meida_source"] = media_device(CAMERA_MOD_ID, CAM_DEV_ID_0, CAM_CHN_ID_0)
    # create meida sink device
    globals()["meida_sink"] = media_device(DISPLAY_MOD_ID, DISPLAY_DEV_ID, DISPLAY_CHN_VIDEO1)
    # create meida link
    media.create_link(meida_source, meida_sink)
    # set display plane with video channel
    display.set_plane(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, PIXEL_FORMAT_YVU_PLANAR_420, DISPLAY_MIRROR_NONE, DISPLAY_CHN_VIDEO1)
    # media buffer init
    media.buffer_init()
    # request media buffer for osd image
    globals()["buffer"] = media.request_buffer(4 * DISPLAY_WIDTH * DISPLAY_HEIGHT)
    # start stream for camera device0
    camera.start_stream(CAM_DEV_ID_0)

def camera_deinit():
    # stop stream for camera device0
    camera.stop_stream(CAM_DEV_ID_0)
    # deinit display
    display.deinit()
    time.sleep_ms(100)
    # release media buffer
    media.release_buffer(globals()["buffer"])
    # destroy media link
    media.destroy_link(globals()["meida_source"], globals()["meida_sink"])
    # deinit media buffer
    media.buffer_deinit()

def draw():
    # create image for drawing
    img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)
    # create image for osd
    buffer = globals()["buffer"]
    osd_img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888, alloc=image.ALLOC_VB, phyaddr=buffer.phys_addr, virtaddr=buffer.virt_addr, poolid=buffer.pool_id)
    osd_img.clear()
    display.show_image(osd_img, 0, 0, DISPLAY_CHN_OSD0)
    fps = time.clock()
    while True:
        fps.tick()
        img.clear()
        for i in range(10):
            x = (urandom.getrandbits(30) % (2*img.width())) - (img.width()//2)
            y = (urandom.getrandbits(30) % (2*img.height())) - (img.height()//2)
            radius_x = urandom.getrandbits(30) % (max(img.height(), img.width())//2)
            radius_y = urandom.getrandbits(30) % (max(img.height(), img.width())//2)
            rot = urandom.getrandbits(30)
            r = (urandom.getrandbits(30) % 127) + 128
            g = (urandom.getrandbits(30) % 127) + 128
            b = (urandom.getrandbits(30) % 127) + 128
            # If the first argument is a scaler then this method expects
            # to see x, y, radius x, and radius y.
            # Otherwise, it expects a (x,y,radius_x,radius_y) tuple.
            img.draw_ellipse(x, y, radius_x, radius_y, rot, color = (r, g, b), thickness = 2, fill = False)
        img.copy_to(osd_img)
        print(fps.fps())

def main():
    camera_is_init = False
    try:
        os.exit_exception_mask(1)
        print("camera init")
        camera_init()
        camera_is_init = True
        os.exit_exception_mask(0)
        print("draw")
        draw()
    except Exception as e:
        os.exit_exception_mask(1)
        print(e)
    finally:
        if camera_is_init:
            print("camera deinit")
            camera_deinit()
        os.exit_exception_mask(0)

if __name__ == "__main__":
    main()
