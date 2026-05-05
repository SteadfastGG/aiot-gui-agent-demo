const output = document.querySelector("#operation-output");
const streamStatus = document.querySelector("#stream-status");
const firmwareVersion = document.querySelector("#firmware-version");

function setOutput(message) {
  output.textContent = message;
}

document.querySelector("[data-testid='device-living_room_camera']").addEventListener("click", () => {
  setOutput("已选择客厅摄像头。");
});

document.querySelector("[data-testid='network-check']").addEventListener("click", () => {
  setOutput("网络检测完成：Wi-Fi 信号弱，RSSI = -78。");
});

document.querySelector("[data-testid='firmware-check']").addEventListener("click", () => {
  setOutput("固件检查完成：当前 2.0.3，发现新版本 2.1.5。");
});

document.querySelector("[data-testid='upgrade-firmware']").addEventListener("click", () => {
  firmwareVersion.textContent = "2.1.5";
  setOutput("模拟固件升级完成：2.0.3 -> 2.1.5。");
});

document.querySelector("[data-testid='restart-device']").addEventListener("click", () => {
  setOutput("设备已完成模拟重启。");
});

document.querySelector("[data-testid='verify-stream']").addEventListener("click", () => {
  streamStatus.textContent = "Recovered";
  setOutput("直播验证完成：远程直播状态恢复。");
});

