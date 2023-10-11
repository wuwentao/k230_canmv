from media.camera import *
# from media.display import *
from media.media import *
from time import *
import time
import image


def canmv_camera_test():
    # CAM_OUTPUT_BUF_NUM = 6
    # CAM_INPUT_BUF_NUM = 4

    print("canmv_camera_test")

    # init(HX8377_V2_MIPI_4LAN_1080X1920_30FPS)

    camera.sensor_init(CAM_DEV_ID_0, CAM_DEFAULT_SENSOR)

    # camera.set_inbufs(CAM_DEV_ID_0, CAM_INPUT_BUF_NUM)

    out_width = 1080
    out_height = 720
    out_width = ALIGN_UP(out_width, 16)

    # set chn0 output yuv420sp
    # camera.set_outbufs(CAM_DEV_ID_0, CAM_CHN_ID_0, CAM_OUTPUT_BUF_NUM)
    camera.set_outsize(CAM_DEV_ID_0, CAM_CHN_ID_0, out_width, out_height)
    camera.set_outfmt(CAM_DEV_ID_0, CAM_CHN_ID_0, PIXEL_FORMAT_YUV_SEMIPLANAR_420)

    out_width = 640
    out_height = 480
    out_width = ALIGN_UP(out_width, 16)

    # set chn1 output rgb888
    # camera.set_outbufs(CAM_DEV_ID_0, CAM_CHN_ID_1, CAM_OUTPUT_BUF_NUM)
    camera.set_outsize(CAM_DEV_ID_0, CAM_CHN_ID_1, out_width, out_height)
    camera.set_outfmt(CAM_DEV_ID_0, CAM_CHN_ID_1, PIXEL_FORMAT_RGB_888)

    # set chn2 output rgb88planar
    # camera.set_outbufs(CAM_DEV_ID_0, CAM_CHN_ID_2, CAM_OUTPUT_BUF_NUM)
    camera.set_outsize(CAM_DEV_ID_0, CAM_CHN_ID_2, out_width, out_height)
    camera.set_outfmt(CAM_DEV_ID_0, CAM_CHN_ID_2, PIXEL_FORMAT_BGR_888_PLANAR)

    # meida_source = media_device(CAMERA_MOD_ID, CAM_DEV_ID_0, CAM_CHN_ID_0)
    # meida_sink = media_device(DISPLAY_MOD_ID, DISPLAY_DEV_ID, DISPLAY_CHN_ID_1)
    # media.create_link(meida_source, meida_sink)

    # meida_source1 = media_device(CAMERA_MOD_ID, CAM_DEV_ID_0, CAM_CHN_ID_1)
    # meida_sink1 = media_device(DISPLAY_MOD_ID, DISPLAY_DEV_ID, DISPLAY_CHN_ID_2)

    # media.create_link(meida_source1, meida_sink1)

    # set_video_plane(0, 160, out_width, out_height, PIXEL_FORMAT_YVU_PLANAR_420, K_ROTATION_0, K_VO_LAYER1)
    # set_video_plane(0, 1040, out_width, out_height, PIXEL_FORMAT_YVU_PLANAR_420, K_ROTATION_0, K_VO_LAYER2)

    ret = media.buffer_init()
    if ret:
        print("canmv_camera_test, buffer init failed")
        return ret

    camera.start_stream(CAM_DEV_ID_0)

    capture_count = 0
    while capture_count < 5:
        time.sleep(1)
        for dev_num in range(CAM_DEV_ID_MAX):
            if not camera.cam_dev[dev_num].dev_attr.dev_enable:
                continue

            for chn_num in range(CAM_CHN_ID_MAX):
                if not camera.cam_dev[dev_num].chn_attr[chn_num].chn_enable:
                    continue

                print(f"canmv_camera_test, dev({dev_num}) chn({chn_num}) capture frame.")

                img = camera.capture_image(dev_num, chn_num)
                if img == -1:
                    print("camera.capture_image failed")
                    continue

                if img.format() == image.YUV420:
                    suffix = "yuv420sp"
                elif img.format() == image.RGB888:
                    suffix = "rgb888"
                elif img.format() == image.RGBP888:
                    suffix = "rgb888p"
                else:
                    suffix = "unkown"

                filename = f"/sdcard/dev_{dev_num:02d}_chn_{chn_num:02d}_{img.width()}x{img.height()}_{capture_count:04d}.{suffix}"
                print("save capture image to file:", filename)

                with open(filename, "wb") as f:
                    if f:
                        img_data = uctypes.bytearray_at(img.virtaddr(), img.size())
                        f.write(img_data)
                    else:
                        print(f"capture_image, open dump file failed({filename})")

                time.sleep(1)

                camera.release_image(dev_num, chn_num, img)

                capture_count += 1

    camera.stop_stream(CAM_DEV_ID_0)

    # kd_mpi_vo_disable_video_layer(1)
    # kd_mpi_vo_disable_video_layer(2)

    # media.destroy_link(meida_source, meida_sink)
    # media.destroy_link(meida_source1, meida_sink1)

    time.sleep(1)

    ret = media.buffer_deinit()
    if ret:
        print("camera test, media_buffer_deinit failed")
        return ret

    print("camera test exit")
    return 0


canmv_camera_test()

