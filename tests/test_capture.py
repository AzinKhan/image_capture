from multiprocessing import Process, Queue

import pytest
import numpy as np

from capture import MotionDetector, ImageInfo

MODULE = 'capture.capture'


class MockCamera:

    def read(self):
        return True, 'frame'


class MockDetector(MotionDetector):

    def __init__(self, mocker):
        mocker.patch(
            f'{MODULE}.createBackgroundSubtractorMOG2'
        )
        super().__init__()

    def _open_camera(self):
        self._camera = MockCamera()


@pytest.fixture
def test_detector(mocker):
    return MockDetector(mocker)


class TestMotionDetector:

    def test_init(self, mocker):
        mock_open = mocker.patch(f'{MODULE}.MotionDetector._open_camera')

        init_args = {
            'cam_num': 1, 'thresh': 20, 'width': 1280, 'height': 960
        }

        detector = MotionDetector(**init_args)
        assert detector.cam_number == init_args['cam_num']
        assert detector.threshold == init_args['thresh']
        assert detector.width == init_args['width']
        assert detector.height == init_args['height']
        mock_open.assert_called()

    def test_open_camera(self, mocker):
        mock_video_capture = mocker.patch(f'{MODULE}.VideoCapture')
        detector = MotionDetector()
        detector._open_camera()

        mock_video_capture.assert_called_with(0)
        # TODO: check camera.set

    def test_average_motion(self, mocker):
        mock_mean = mocker.patch(f'{MODULE}.mean')
        frame = list(range(10))

        MotionDetector._average_motion(frame, 1)
        mock_mean.assert_called_with(frame)

    @pytest.mark.parametrize('return_val, frame', [
        (True, 'frame'),
    ])
    def test_read_camera(self, mocker, return_val, frame, test_detector):
        result_val = test_detector._read_camera()
        assert result_val == return_val
        if return_val:
            assert test_detector._current_frame.frame == frame

    def test_detect_motion(self, mocker, test_detector):
        test_image_info = ImageInfo()

        foreground = np.random.random((1024, 768))
        test_detector._current_frame = test_image_info
        mock_bg_apply = mocker.patch.object(
            test_detector._bg,
            'apply',
            return_value=foreground
        )

        mock_average = mocker.patch.object(
            test_detector,
            '_average_motion',
        )

        test_detector._detect_motion()

        mock_bg_apply.assert_called_with(test_image_info.frame)
        mock_average.assert_called_with(foreground, 0)

    def test_run(self, mocker, test_detector):
        mocker.patch.object(
            test_detector,
            '_read_camera',
            return_value=True
        )
        mocker.patch.object(
            test_detector,
            '_detect_motion',
        )
        current_frame = ImageInfo()
        image = np.random.random((1024, 768))
        current_frame.frame = image
        current_frame.motion_val = test_detector.threshold + 10
        test_detector._current_frame = current_frame

        image_queue = Queue()

        detector_process = Process(
            target=test_detector.run, args=(image_queue,)
        )
        detector_process.daemon = True
        detector_process.start()

        img = image_queue.get()
        detector_process.terminate()
        detector_process.join()

        assert img.frame.all() == image.all()
