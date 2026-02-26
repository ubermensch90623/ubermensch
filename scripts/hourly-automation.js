#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const configPath = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.resolve(__dirname, "automation-config.json");

const loadConfig = () => {
  if (!fs.existsSync(configPath)) {
    console.error(`설정 파일이 없습니다: ${configPath}`);
    console.error("예시 파일을 복사해 automation-config.json으로 설정하세요.");
    process.exit(1);
  }

  const raw = fs.readFileSync(configPath, "utf8");
  return JSON.parse(raw);
};

const formatTimestamp = (timezone) => {
  try {
    return new Intl.DateTimeFormat("ko-KR", {
      dateStyle: "medium",
      timeStyle: "medium",
      timeZone: timezone || "Asia/Seoul",
    }).format(new Date());
  } catch (error) {
    return new Date().toISOString();
  }
};

const run = () => {
  const config = loadConfig();
  const timestamp = formatTimestamp(config.timezone);

  console.log("========================================");
  console.log(`[${timestamp}] 자동화 작업 시작`);
  console.log("========================================");

  const links = config.links || {};
  const tasks = config.tasks || [];

  if (Object.keys(links).length) {
    console.log("연결된 링크 목록:");
    Object.entries(links).forEach(([key, value]) => {
      console.log(`- ${key}: ${value}`);
    });
  } else {
    console.log("연결된 링크가 없습니다. automation-config.json을 확인하세요.");
  }

  if (tasks.length) {
    console.log("\n예약된 자동화 작업:");
    tasks.forEach((task, index) => {
      console.log(`${index + 1}. ${task.id} - ${task.description}`);
    });
  } else {
    console.log("\n등록된 작업이 없습니다. automation-config.json을 확인하세요.");
  }

  console.log("\n실제 API 연동/작업 실행은 별도 구현이 필요합니다.");
  console.log("Notion/Google API 연결 정보를 추가하면 자동화 범위를 확장할 수 있습니다.");
};

run();
