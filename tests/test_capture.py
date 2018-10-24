import pytest

from capture import MotionDetector

MODULE = 'capture.capture'


class MockCamera:

    def read(self):
        return True, 'frame'


class MockDetector(MotionDetector):

    def __init__(self):
        super().__init__()

    def _open_camera(self):
        self._camera = MockCamera()


@pytest.fixture
def test_detector():
    return MockDetector()


class TestMotionDetector:

    def test_init(self, mocker):
        mock_open = mocker.patch(f'{MODULE}.MotionDetector._open_camera')
        mock_subtractor = mocker.patch(
            f'{MODULE}.createBackgroundSubtractorMOG2'
        )

        init_args = {
            'cam_num': 1, 'thresh': 20, 'width': 1280, 'height': 960
        }

        detector = MotionDetector(**init_args)
        assert detector.cam_number == init_args['cam_num']
        assert detector.threshold == init_args['thresh']
        assert detector.width == init_args['width']
        assert detector.height == init_args['height']
        mock_open.assert_called()
        mock_subtractor.assert_called()

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
        result_val = test_detector._read__camera()
        assert result_val == return_val
        if return_val:
            assert test_detector._current_frame.frame == frame
