function xorEncryptBuffer(buffer, key) {
    const keyBuffer = Buffer.from(key, "utf-8");
    const result = Buffer.alloc(buffer.length);

    for (let i = 0; i < buffer.length; i++) {
        result[i] = buffer[i] ^ keyBuffer[i % keyBuffer.length];
    }
    return result;
}

// 使用例
const key = "this is a key";
const text = "appple is a red fruit";

// 文字列をバッファに変換
const buffer = Buffer.from(text, "utf-8");

// 暗号化
const encryptedBuffer = xorEncryptBuffer(buffer, key);
console.log("暗号化:", encryptedBuffer.toString("hex"));

// 復号化（暗号化と同じ関数を使用）
const decryptedBuffer = xorEncryptBuffer(encryptedBuffer, key);
console.log("復号化:", decryptedBuffer.toString("utf-8"));
