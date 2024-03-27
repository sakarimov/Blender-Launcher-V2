from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from operator import attrgetter

from semver import Version


@dataclass(frozen=True)
class VersionSearch:
    major: int | str
    minor: int | str
    patch: int | str

    def __post_init__(self):
        for pos in (self.major, self.minor, self.patch):
            if isinstance(pos, str) and pos not in ["^", "*", "-"]:
                raise ValueError(f'{pos} must be in ["^", "*", "-"]')

    @classmethod
    def default(cls):
        return cls("^", "^", "^")


@dataclass(frozen=True)
class VersionMatcher:
    versions: tuple[Version, ...]

    @staticmethod
    @cache
    def _get_max_version(vs: tuple[Version], place: str):
        assert place in ("major", "minor", "patch")
        getter = attrgetter(place)
        return max(vs, key=getter)

    @staticmethod
    @cache
    def _get_min_version(vs: tuple[Version], place: str):
        assert place in ("major", "minor", "patch")
        getter = attrgetter(place)
        return min(vs, key=getter)

    def match(self, s: VersionSearch) -> tuple[Version, ...]:
        versions = self.versions
        for place in ("major", "minor", "patch"):
            checkers = []
            getter = attrgetter(place)
            p: str | int = getter(s)
            if p == "^":

                def _check_max(v, getter=getter, place=place, versions=versions):
                    return getter(v) == getter(self._get_max_version(versions, place))

                checkers.append(_check_max)
            elif p == "*":
                pass
            elif p == "-":

                def _check_min(v, getter=getter, place=place, versions=versions):
                    return getter(v) == getter(self._get_min_version(versions, place))

                checkers.append(_check_min)
            else:

                def _check_eq(v, getter=getter, p=p):
                    return getter(v) == p

                checkers.append(_check_eq)

            versions = tuple(v for v in versions if all(checker(v) for checker in checkers))
            if len(versions) == 1:
                return versions

        return versions


if __name__ == "__main__":
    versions = (
        Version(major=4, minor=2, patch=0, prerelease="alpha", build=None),
        Version(major=4, minor=1, patch=0, prerelease="candidate", build=None),
        Version(major=3, minor=3, patch=18, prerelease=None, build=None),
        Version(major=3, minor=6, patch=11, prerelease=None, build=None),
        Version(major=4, minor=1, patch=0, prerelease=None, build=None),
        Version(major=4, minor=2, patch=0, prerelease=None, build=None),
        Version(major=3, minor=3, patch=18, prerelease="candidate", build=None),
        Version(major=3, minor=6, patch=11, prerelease="candidate", build=None),
        Version(major=4, minor=1, patch=0, prerelease="candidate", build=None),
        Version(major=4, minor=2, patch=0, prerelease="alpha", build=None),
        Version(major=4, minor=2, patch=0, prerelease="brush-assets-project", build=None),
        Version(major=4, minor=2, patch=0, prerelease="universal-scene-description", build=None),
        Version(major=3, minor=3, patch=16, prerelease=None, build=None),
        Version(major=3, minor=6, patch=10, prerelease=None, build=None),
        Version(major=3, minor=6, patch=9, prerelease=None, build=None),
        Version(major=4, minor=0, patch=2, prerelease=None, build=None),
        Version(major=3, minor=3, patch=16, prerelease="PR119165", build=None),
        Version(major=3, minor=6, patch=10, prerelease="PR119379", build=None),
        Version(major=3, minor=6, patch=9, prerelease="PR117027", build=None),
        Version(major=4, minor=0, patch=2, prerelease="PR117059", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR104456", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR106303", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR113107", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR113115", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR113122", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR114545", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR115525", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR116724", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR116987", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117096", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117311", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117341", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117390", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117414", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117428", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117513", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117593", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117669", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR117700", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118112", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118114", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118502", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118540", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118562", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR118699", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR119089", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR119315", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR119448", build=None),
        Version(major=4, minor=1, patch=0, prerelease="PR119476", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR104665", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR109522", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR110156", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR116109", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR116149", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR116646", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR117114", build=None),
        Version(major=4, minor=2, patch=0, prerelease="PR117287", build=None),
    )
    matcher = VersionMatcher(versions)
    search = VersionSearch(3, "-", "*")

    from pprint import pprint

    pprint(matcher.match(search))
