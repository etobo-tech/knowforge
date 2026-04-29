const BYTES_PER_KIB = 1024;
const KIB_PER_MIB = 1024;

const DEFAULT_MAX_UPLOAD_SIZE_MIB = 2;

function getMaxUploadSizeMib(): number {
  const raw = (process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE_MIB ?? "").trim();
  const parsed = Number.parseInt(raw, 10);
  if (Number.isFinite(parsed) && parsed >= 1) {
    return parsed;
  }
  return DEFAULT_MAX_UPLOAD_SIZE_MIB;
}

export function getMaxUploadBytes(): number {
  return getMaxUploadSizeMib() * KIB_PER_MIB * BYTES_PER_KIB;
}

export function getMaxUploadSizeMibForUi(): number {
  return getMaxUploadSizeMib();
}
