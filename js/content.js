// 内蔵の教材データ（Lemma では自動判定つきの内蔵問題と旧式の解法カードを置いていた場所）
// EUCLEA には内蔵問題がない。問題はすべて問題管理表から作る data/、解法カードは content/techniques.json。
// 他のモジュールが同じ名前で読むため、空の一覧として残している。
export const FILE_VERSION = '0.27.1';

export const SUBJECTS = [];
export const UNITS = [];
export const LEVELS = {};
export const CARDS = [];
export const PROBLEMS = [];

export const cardById = {};
export const problemById = {};
export const unitById = {};
export const subjectById = {};
export function problemsFor() { return []; }
export function unitOf(p) { return cardById[p.cards[0]].unit; }
export function subjectOf(p) { return unitById[unitOf(p)].subject; }
