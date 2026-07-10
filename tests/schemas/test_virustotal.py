from bot.schemas.virustotal import VTFileVerdict, VTUrlVerdict


def test_vt_file_verdict_defaults_status_unknown_when_not_specified():
    verdict = VTFileVerdict(sha256="a" * 64)
    assert verdict.status == "unknown"
    assert verdict.malicious_count == 0
    assert verdict.total_engines == 0
    assert verdict.detection_names == []


def test_vt_url_verdict_holds_malicious_status():
    verdict = VTUrlVerdict(
        url="https://example.com",
        status="malicious",
        malicious_count=12,
        total_engines=70,
        permalink="https://virustotal.com/x",
        detection_names=["Phishing.Generic", "Malware.Generic"],
    )
    assert verdict.status == "malicious"
    assert verdict.malicious_count == 12
    assert verdict.detection_names == ["Phishing.Generic", "Malware.Generic"]
