# Plan A: Linguistic Data Analysis II — コース設計

## コースの基本情報

- **対象**: 応用言語学修士課程の学生
- **前提知識**: Python経験なし。Linguistic Data Analysis Iの続編だが、Iを未履修の学生にも対応する必要あり
- **形式**: 5日間集中講義、1日3コマ（導入→チュートリアル→応用ハンズオン）
- **担当**: Masaki（東北大学）
- **LDA Iサイト**: <https://egumasa.github.io/linguistic-data-analysis-I/>

## コースのビジョン

LLMをツールとして使いながら言語データ分析を行い、その過程で以下の4スキルを体得させる：

1. **正解データ構築**（アノテーションスキーム設計、アノテーション、品質管理）
2. **プロンプト設計**（ゼロショット・フューショット、反復改善）
3. **評価の実行**（precision, recall, F1, confusion matrix）
4. **結果の解釈**（エラー分析、プロンプト改善への接続）

これらを習得すれば、コース後に自分のプロジェクトに応用できる。

## コース設計方針

### 自作チュートリアル中心

「LLMをツールとして使いながら言語データ分析を学ぶ」にドンピシャの教科書は現時点で存在しない。自作チュートリアルを軸に、論文を理論的裏付けとして統合する。読み物は重くしない。

### スキル習得型 ＋ 足場付きミニプロジェクト

5日間・Python未経験・LDA I未履修者混在という条件では、フルのプロジェクト型はリスクが高い（Day 2-3の内容を吸収しきれない、データ準備に時間がかかる、グループ内力量差）。一方、スキル習得だけだと「LDA IのLLM版」で終わる危険がある。

**方針**: Day 1-3で全員同じチュートリアルを通して4スキルを習得し、Day 4-5でこちらが用意したデータ・タスクセット（語彙分析版・文法分析版など）から選ばせるミニプロジェクト。学生が自由に動かせる部分はプロンプト設計と結果の解釈に絞る。

### こちらが準備するインフラ

- **評価ツール**: scikit-learnの`classification_report` + `confusion_matrix`をラップしたColabノートブック。学生はCSV（`gold_label`, `llm_output`）を投げるだけで評価指標が返る
- **LangChainは不要**: 抽象化レイヤーがPython未経験者にはブラックボックスになる。「正解 vs LLM出力」の比較にはscikit-learnで十分かつ透明
- **データセット**: 語彙・文法など分析領域ごとに、アノテーション済みのデータとタスク定義を用意
- **フォーマット**: 「このデータに対して、このプロンプトを設計し、この評価指標で報告せよ」の固定フレーム

## 5日間の構成

### Day 1: LLM × 言語データの初体験

| コマ | 内容 | 詳細 |
|------|------|------|
| コマ1 | 導入 | LLM×言語データ分析とは何か、コースの全体像、LDA Iとの接続 |
| コマ2 | チュートリアル | チャットUI（Claude.ai / ChatGPT）で10-15文の小規模データを分類 → 手動で正解と比較。LLMで言語データを分析できるという初体験 |
| コマ3 | テーマ決定 | ミニプロジェクトのテーマ・タスク選択 + グループ編成 |

**Day 1 コマ2の設計意図**:
- AntConc ChatAIはOpenAI APIキーが必要で事務的負担が大きいため、初日には使わない
- 学習者英語のエラータイプ分類など、身近なタスクで「LLMに言語データを投げて結果を検証する」体験を作る
- この体験がDay 2-3の形式的な評価指標（precision/recall/F1）の動機づけになる

### Day 2: 「良いデータ」の作法

| コマ | 内容 | 詳細 |
|------|------|------|
| コマ1 | 導入 | アノテーションの原則、「良い研究にはどういうデータとプロセスが必要か」 |
| コマ2 | チュートリアル | こちらが用意したアノテーションスキームで20サンプルをアノテーション → 一致率計算 → LLMにも同じタスクをやらせて比較 |
| コマ3 | 応用ハンズオン | precision / recall / F1 / confusion matrixの概念導入と実践（Colab演習） |

**コア論文**: Abdurahman et al. (2025) + Eguchi & Kyle (2024)

**設計上の注意**: Day 2は最も密度が高い。アノテーション演習はゼロからスキーム設計させるのではなく、用意済みスキームに対して少量サンプルをアノテーションさせる方が現実的。

### Day 3: プロンプト設計と反復改善

| コマ | 内容 | 詳細 |
|------|------|------|
| コマ1 | 導入 | プロンプト設計の原則、ゼロショット vs フューショット |
| コマ2 | チュートリアル | Colab経由で実際の言語データに対してLLMで分類 → 評価指標で検証 |
| コマ3 | 応用ハンズオン | プロンプト改善 → 再評価のサイクルを2-3回転 |

### Day 4: 方法論的考慮 + プロジェクト

| コマ | 内容 | 詳細 |
|------|------|------|
| コマ1 | 追加トピック | 再現性（モデル・バージョン固定、プロンプトの完全記録、温度パラメータ）、LLMの限界（ハルシネーション、言語間格差）、倫理（データプライバシー、LLM出力の著者性）→ 報告チェックリスト配布 |
| コマ2-3 | プロジェクト作業 | グループプロジェクト |

### Day 5: 仕上げ + 発表

| コマ | 内容 | 詳細 |
|------|------|------|
| コマ1-2 | プロジェクト準備 | 最終的な評価実行、発表資料作成 |
| コマ3 | 発表・ディスカッション | |

## LLMアクセス方法

**段階的アプローチ**:

- **Day 1-2**: チャットUI（Claude.ai / ChatGPT）で手動操作。少量データでプロンプトの試行錯誤を体感
- **Day 3以降**: こちらが用意したColabノートブックでAPI呼び出し。学生はプロンプト文字列とデータCSVだけを差し替える

**Colabノートブックの構造**:

```
セル1: APIキー設定（教員が共有キーを事前設定）
セル2: データ読み込み（CSVアップロード）
セル3: プロンプトテンプレート（★学生が編集する唯一の箇所★）
セル4: LLM呼び出し＋結果保存（実行するだけ）
セル5: 評価指標の表示（classification_report + confusion_matrix）
```

APIキーは教員管理にして学生の負担をゼロにする。

## ミニプロジェクトのタスクセット候補

| タスク | 具体例 | 難易度 |
|--------|--------|--------|
| 語彙分析 | 学術語彙 vs 一般語彙の分類 | ★☆☆ |
| 文法分析 | 時制・相のエラー検出 | ★★☆ |
| 談話分析 | Engagement（Martin & White）のカテゴリ分類 | ★★★ |
| 語用論 | 発話行為の分類（依頼・謝罪・提案など） | ★★☆ |
| 感情・スタンス | レビューテキストのセンチメント分類 | ★☆☆ |

各タスクに「50-100サンプルのアノテーション済みデータ + タスク定義書 + ベースラインプロンプト」を用意。

## 評価ツールの実装

Colabノートブック1枚、2層構造：

- **層1（全員必須）**: CSVアップロード → `classification_report` + confusion matrixヒートマップ可視化。5セル以内
- **層2（発展）**: クラスごとの誤分類例をランダムに5件表示。エラー分析 → プロンプト改善のループに直結

## 教材

### コア論文（チュートリアルに統合）

| 論文 | 役割 | 配置 |
|------|------|------|
| Abdurahman et al. (2025) "A Primer for Evaluating Large Language Models in Social-Science Research" | LLMを研究ツールとして使う際の方法論チェックリスト（再現性、プロンプト設計、モデル選択、評価） | Day 2 |
| Eguchi & Kyle (2024) "Building custom NLP tools to annotate discourse-functional features for second language writing research: A tutorial" | 応用言語学におけるNLPツール構築パイプライン全体像（アノテーション→モデル→評価→公開） | Day 2 |
| Anthony (2025) "Integrating AI technology into corpus-based language learning through ChatAI" | コーパス言語学とLLMの統合。AntConc + ChatAIの裏付け | Day 1付近 |
| Uchida (2024) "Using early LLMs for corpus linguistics" | LLMの可能性と限界を実証的に示す。批判的視点の導入 | Day 1付近 |

### 参考資料（必要に応じて参照）

| 資料 | 役割 |
|------|------|
| Vajjala et al. (2020) *Practical NLP* (O'Reilly) | NLPパイプラインの概念的全体像（Ch.2）、テキスト分類の評価指標（Ch.4）。コードは追わず概念のみ |
| Hvitfeldt & Silge (2022) *Supervised ML for Text Analysis in R* (無料: smltar.com) | MLの「作法」の説明がクリア。Rベースだが概念参照用 |
| Jurafsky & Martin SLP3 draft (無料: slp3) | 学生が深掘りしたい場合の参照先 |

### 検討したが採用しなかったもの

- Bird et al. *NLP with Python* (NLTK Book) — LLM以前の内容で補完が必要すぎる
- Tunstall et al. *NLP with Transformers* — Python経験前提で5日間には重い
- McEnery & Hardie *Corpus Linguistics* — 理論的土台としては良いがLLMの話がない
- Bender *Linguistic Fundamentals for NLP* — 言語学→NLPの橋渡しとしては良いがスコープが違う

## LDA Iとの接続

TAALED / TAALES / TAASCは「ルールベース・特徴量ベースの自動分析ツール」として位置づけ、LDA IIでは「LLMベースの分析」との対比として導入：

- Day 1の導入で「LDA Iで学んだ指標（語彙多様性、統語的複雑さなど）をLLMはどう扱えるか？」と問いかける
- 「TAALES/TAASCが数値化する特徴量 vs LLMが文脈的に判断する分類」の違いを明示

## リスクと注意点

### Day 2の時間圧縮リスク

Day 2は最も密度が高い（アノテーションスキーム→アノテーション実施→一致率→LLM比較→評価指標導入）。アノテーション演習は用意済みスキームに対して少量サンプルを行わせる設計にする。

### Day 3→4の接続

Day 3のプロンプト改善サイクルからDay 4のプロジェクトへの切り替えが曖昧になりうる。Day 4コマ1で「プロジェクト報告に必要な要素」のチェックリストを配布して切り替えを明確化する。

### グループ編成

LDA I既修者と未履修者が混在するため、各グループに最低1名の既修者を配置。Day 1のうちに編成を完了する。

## 関連リソース

- LDA I コースサイト: <https://egumasa.github.io/linguistic-data-analysis-I/>
- AntConc 4.3 (ChatAI搭載): <https://www.laurenceanthony.net/software/antconc/>
- Sydney Corpus Lab "Generative AI in corpus linguistics: A synthesis" (2025): <https://sydneycorpuslab.com/generative-ai-in-corpus-linguistics-a-synthesis/>
- Jurafsky & Martin SLP3 draft: <https://web.stanford.edu/~jurafsky/slp3/>
- Supervised ML for Text Analysis in R (無料): <https://smltar.com/>

## 未決定事項（残課題）

- [ ] AntConc ChatAIのAPIキー問題: 学生にOpenAI APIキーを用意させる必要があるかどうか（→ Day 4以降の発展的リソースとして扱う案）
- [ ] ミニプロジェクトの最終タスクセット: 上記候補から実際に何を用意するか
- [ ] Colabノートブックの実装・テスト
- [ ] Day 2のアノテーション用スキームとサンプルデータの準備
- [ ] 報告チェックリストの作成
