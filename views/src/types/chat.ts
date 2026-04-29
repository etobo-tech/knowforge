export type Role = "user" | "assistant";

export type Citation = {
  fileId: string;
  chunkId: string;
};

export type Message = {
  id: string;
  role: Role;
  text: string;
  createdAt: number;
  kind?: "normal" | "error";
  citations?: Citation[];
};
