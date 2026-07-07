from __future__ import annotations

from typing import Any, Final, Optional

import attr
from reactivex import Observable, abc, create
from reactivex.disposable import CompositeDisposable, Disposable, SerialDisposable
from reactivex.scheduler.currentthreadscheduler import CurrentThreadScheduler

from blrec.bili.typing import ApiPlatform, QualityNumber, StreamFormat

__all__ = ('StreamParamHolder',)


@attr.s(auto_attribs=True, frozen=True, slots=True)
class StreamParams:
    stream_format: StreamFormat
    quality_number: QualityNumber
    api_platform: ApiPlatform
    codec_unavailable: bool


class StreamParamHolder:
    def __init__(
        self,
        *,
        stream_format: StreamFormat = 'flv',
        quality_number: QualityNumber = 10000,
        api_platform: ApiPlatform = 'web',
        codec_unavailable: bool = False
    ) -> None:
        super().__init__()
        self._stream_format: Final = stream_format
        self._quality_number = quality_number
        self._real_quality_number: Optional[QualityNumber] = None
        self._api_platform: ApiPlatform = api_platform
        self._codec_unavailable: bool = codec_unavailable
        self._cancelled: bool = False

    def reset(self) -> None:
        self._real_quality_number = None
        self._api_platform = 'web'
        self._codec_unavailable = False
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def stream_format(self) -> StreamFormat:
        return self._stream_format

    @property
    def quality_number(self) -> QualityNumber:
        return self._quality_number

    @quality_number.setter
    def quality_number(self, value: QualityNumber) -> None:
        self._quality_number = value

    @property
    def real_quality_number(self) -> QualityNumber:
        return self._real_quality_number or self._quality_number

    @property
    def codec_unavailable(self) -> bool:
        return self._codec_unavailable

    @codec_unavailable.setter
    def codec_unavailable(self, value: bool) -> None:
        self._codec_unavailable = value

    def fall_back_quality(self, qn) -> None:
        if qn == 150 or qn == 10000:
            self._real_quality_number = 250
        elif qn == 25000:
            self._real_quality_number = 10000
        else:
            self._real_quality_number = 10000
        return self._real_quality_number

    def rotate_api_platform(self) -> None:
        if self._api_platform == 'android':
            self._api_platform = 'web'
        else:
            self._api_platform = 'android'

    def get_stream_params(self) -> Observable[StreamParams]:
        self.reset()

        def subscribe(
            observer: abc.ObserverBase[StreamParams],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or CurrentThreadScheduler.singleton()

            disposed = False
            cancelable = SerialDisposable()

            def action(
                scheduler: abc.SchedulerBase, state: Optional[Any] = None
            ) -> None:
                if self._cancelled or disposed:
                    return

                params = StreamParams(
                    stream_format=self._stream_format,
                    quality_number=self._real_quality_number or self._quality_number,
                    api_platform=self._api_platform,
                    codec_unavailable=self._codec_unavailable
                )
                observer.on_next(params)

            cancelable.disposable = _scheduler.schedule(action)

            def dispose() -> None:
                nonlocal disposed
                disposed = True

            return CompositeDisposable(cancelable, Disposable(dispose))

        return create(subscribe)
