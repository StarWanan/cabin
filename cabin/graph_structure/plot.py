import json
from graphviz import Digraph

# 读取 JSON 配置
config = {
  "params": {
    "channel_id": 94349602534,
    "channel_app": "tiktok",
    "module_inherit": "__tiktok_growth__"
  },
  "modules": {
    "user_region_filter": {
      "clazz": "qrec_service::common::UserRegionFilter"
    },
    "request": {
      "clazz": "qrec_service::recommend::RegularRequest",
      "deps": [
        "user_region_filter"
      ],
      "args": {
        "allow_failure": "false"
      }
    },
    "impression_container_retriever": {
      "clazz": "qrec_service::common::ImpressionContainerRetriever",
      "deps": [
        "request"
      ]
    },
    "bg_session_gremlin_retriever": {
      "clazz": "qrec_service::recommend::BgSessionGremlinRetriever",
      "if": "logged_in",
      "deps": [
        "request"
      ]
    },
    "weiss_predict_ip_port_retriever": {
      "clazz": "qrec_service::common::PredictIPPortRetriever",
      "deps": [
        "request"
      ],
      "args": {
        "sla_score": 0.3
      }
    },
    "user_feedback_retriever": {
      "clazz": "qrec_service::recommend::UserFeedbackRetriever",
      "if": "logged_in",
      "deps": [
        "request"
      ]
    },
    "context_bert_embedding_retriever": {
      "clazz": "qrec_service::common::ContextBertEmbeddingRetriever",
      "if": "logged_in",
      "deps": [
        "bg_session_gremlin_retriever",
        "user_feedback_retriever"
      ]
    },
    "go_user_feature_retriever": {
      "clazz": "qrec_service::common::GoUserFeatureRetriever",
      "if": "logged_in",
      "deps": [
        "request"
      ]
    },
    "weiss_embedding_retriever": {
      "clazz": "qrec_service::common::WeissEmbeddingRetriever",
      "if": "logged_in",
      "deps": [
        "bg_session_gremlin_retriever",
        "go_user_feature_retriever",
        "impression_container_retriever",
        "weiss_predict_ip_port_retriever"
      ]
    },
    "search_history_bert_recall": {
      "clazz": "qrec_service::common::VikingSimpleBatchRecall",
      "if": "logged_in",
      "deps": [
        "context_bert_embedding_retriever",
        "impression_container_retriever"
      ]
    },
    "viking_base_recall": {
      "clazz": "qrec_service::common::VikingSimpleRecall",
      "if": "logged_in",
      "deps": [
        "weiss_embedding_retriever",
        "impression_container_retriever"
      ]
    },
    "viking_click_recall": {
      "clazz": "qrec_service::common::VikingSimpleRecall",
      "if": "logged_in",
      "deps": [
        "weiss_embedding_retriever",
        "impression_container_retriever"
      ]
    },
    "global_hot_abase_recall": {
      "clazz": "qrec_service::recommend::SummarizedPosteriorRecall",
      "if": "logged_in",
      "deps": [
        "weiss_embedding_retriever",
        "impression_container_retriever"
      ]
    },
    "personalized_shortterm_recall": {
      "clazz": "qrec_service::common::VikingSimpleRecall",
      "if": "logged_in",
      "deps": [
        "weiss_embedding_retriever",
        "impression_container_retriever"
      ]
    },
    "darwin_passive_search_click_recall": {
      "clazz": "weiss_service::DarwinInvertedRecall",
      "if": "not logged_in",
      "deps": [
        "request"
      ]
    },
    "snake_merger": {
      "clazz": "qrec_service::common::SnakeMerger",
      "deps": [
        "personalized_shortterm_recall",
        "search_history_bert_recall",
        "viking_base_recall",
        "viking_click_recall",
        "global_hot_abase_recall",
        "darwin_passive_search_click_recall"
      ]
    },
    "group_info_retriever": {
      "clazz": "qrec_service::common::GroupInfoRetriever",
      "deps": [
        "snake_merger"
      ],
      "args": {
        "allow_failure": "false"
      }
    },
    "combine_profile_retriever": {
      "clazz": "qrec_service::common::CombineProfileRetriever",
      "deps": [
        "snake_merger"
      ]
    },
    "determine_recent_click_method": {
      "clazz": "qrec_service::recommend::DetermineRecentClickMethod",
      "if": "not logged_in",
      "deps": [
        "group_info_retriever"
      ]
    },
    "determine_click_dedup_method": {
      "clazz": "qrec_service::recommend::DetermineClickDedupMethod",
      "if": "logged_in",
      "deps": [
        "group_info_retriever"
      ]
    },
    "determine_review_level_method": {
      "clazz": "qrec_service::common::DetermineReviewLevelMethod",
      "deps": [
        "group_info_retriever"
      ]
    },
    "determine_search_intent_method": {
      "clazz": "qrec_service::recommend::DetermineSearchIntentMethod",
      "deps": [
        "group_info_retriever"
      ]
    },
    "determine_format_method": {
      "clazz": "qrec_service::recommend::DetermineFormatMethod",
      "deps": [
        "group_info_retriever"
      ]
    },
    "debug_item_query_retriever": {
      "clazz": "qrec_service::common::DebugItemQueryRetriever",
      "deps": [
        "group_info_retriever"
      ]
    },
    "filter_executor": {
      "clazz": "qrec_service::common::FilterExecutor",
      "deps": [
        "determine_review_level_method",
        "determine_search_intent_method",
        "determine_format_method"
      ]
    },
    "impression_filter": {
      "clazz": "qrec_service::common::ImpressionFilter",
      "deps": [
        "determine_click_dedup_method",
        "filter_executor"
      ]
    },
    "determine_per_user_impression_num_method": {
      "clazz": "qrec_service::recommend::DetermineImpressionThisUserMethod",
      "if": "logged_in",
      "deps": [
        "impression_filter"
      ]
    },
    "weiss_extract_retriever": {
      "clazz": "qrec_service::recommend::WeissExtractRetriever",
      "if": "logged_in",
      "deps": [
        "determine_per_user_impression_num_method"
      ]
    },
    "marine_roughsort_sorter": {
      "clazz": "qrec_service::common::MarineRoughsortSorter",
      "if": "logged_in",
      "deps": [
        "weiss_extract_retriever"
      ]
    },
    "rough_predict_sorter": {
      "clazz": "qrec_service::recommend::WeissRoughPredictSorter",
      "if": "logged_in",
      "deps": [
        "determine_per_user_impression_num_method",
        "weiss_predict_ip_port_retriever"
      ]
    },
    "rule_query_keyword_label": {
      "clazz": "qrec_service::recommend::RuleQueryKeywordLabel",
      "deps": [
        "impression_filter"
      ]
    },
    "rule_query_term_label": {
      "clazz": "qrec_service::recommend::RuleQueryTermLabel",
      "deps": [
        "impression_filter"
      ]
    },
    "after_roughsort_ranking_rule": {
      "clazz": "qrec_service::recommend::RankingRule",
      "deps": [
        "rule_query_keyword_label",
        "rule_query_term_label",
        "rough_predict_sorter",
        "marine_roughsort_sorter"
      ]
    },
    "pre_predict_cut_method": {
      "clazz": "qrec_service::common::AssuranceCutMethod",
      "if": "logged_in",
      "deps": [
        "after_roughsort_ranking_rule"
      ]
    },
    "predict_sorter": {
      "clazz": "qrec_service::recommend::WeissPredictSorter",
      "deps": [
        "combine_profile_retriever",
        "pre_predict_cut_method"
      ]
    },
    "online_emoji_filter": {
      "clazz": "qrec_service::recommend::OnlineEmojiFilter",
      "deps": [
        "predict_sorter"
      ]
    },
    "rule_recall_reason_label": {
      "clazz": "qrec_service::common::RuleRecallReasonLabel",
      "deps": [
        "online_emoji_filter",
        "rpc_tns_filter",
        "reviewed_wordlist_filter"
      ]
    },
    "rpc_tns_filter": {
      "clazz": "qrec_service::recommend::RpcTnsFilter",
      "deps": [
        "predict_sorter"
      ]
    },
    "reviewed_wordlist_filter": {
      "clazz": "qrec_service::recommend::LataXWordlistFilter",
      "deps": [
        "predict_sorter"
      ]
    },
    "bert_embedding_retriever": {
      "clazz": "qrec_service::common::BertEmbeddingRetriever",
      "deps": [
        "predict_sorter"
      ]
    },
    "feedback_query_filter": {
      "clazz": "qrec_service::recommend::FeedbackQueryFilter",
      "if": "logged_in",
      "deps": [
        "bert_embedding_retriever"
      ]
    },
    "bert_distance_scatter_label": {
      "clazz": "qrec_service::common::BertDistanceScatterLabel",
      "deps": [
        "feedback_query_filter"
      ]
    },
    "rule_edit_distance_label": {
      "clazz": "qrec_service::common::RuleEditDistanceLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "rule_prepostfix_label": {
      "clazz": "qrec_service::recommend::RulePrepostfixLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "rule_jaccard_similarity_label": {
      "clazz": "qrec_service::recommend::RuleJaccardSimilarityLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "rule_lcs_label": {
      "clazz": "qrec_service::recommend::RuleLcsLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "rule_query_stem_label": {
      "clazz": "qrec_service::recommend::RuleQueryStemLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "ner_scatter_label": {
      "clazz": "qrec_service::common::NerScatterLabel",
      "deps": [
        "rule_recall_reason_label"
      ]
    },
    "ranking_rule": {
      "clazz": "qrec_service::recommend::RankingRule",
      "if": "logged_in",
      "deps": [
        "rule_lcs_label",
        "rule_jaccard_similarity_label",
        "rule_prepostfix_label",
        "bert_distance_scatter_label",
        "rule_edit_distance_label",
        "ner_scatter_label",
        "rule_query_stem_label"
      ]
    },
    "not_log_in_user_ranking_rule": {
      "clazz": "qrec_service::recommend::RankingRule",
      "if": "not logged_in",
      "deps": [
        "determine_recent_click_method",
        "ranking_rule"
      ]
    },
    "response": {
      "clazz": "qrec_service::recommend::RegularResponse",
      "deps": [
        "not_log_in_user_ranking_rule"
      ]
    },
    "predict_ack": {
      "clazz": "qrec_service::recommend::WeissPredictAck",
      "deps": [
        "response"
      ]
    },
    "group_miss_sinker": {
      "clazz": "qrec_service::common::GroupMissSinker",
      "deps": [
        "response"
      ]
    },
    "impression_container_sinker": {
      "clazz": "qrec_service::common::ImpressionContainerSinker",
      "deps": [
        "response"
      ]
    },
    "debug_response": {
      "clazz": "qrec_service::recommend::RegularDebugResponse",
      "deps": [
        "response",
        "debug_item_query_retriever"
      ],
      "args": {
        "always_run": "true"
      }
    }
  }
}

# 创建有向图
dot = Digraph(comment='TikTok Recommendation DAG')
dot.attr(rankdir='LR', size='50,50')  # 从左到右布局

# 解析模块和依赖关系
modules = config["modules"]
edges = set()  # 用集合避免重复边

for module_name, module_config in modules.items():
    # 添加节点
    dot.node(module_name, shape='box', style='rounded,filled', fillcolor='#e0f0ff')

    # 添加依赖边
    deps = module_config.get("deps", [])
    for dep in deps:
        edges.add((dep, module_name))

# 添加所有边
for src, dst in edges:
    dot.edge(src, dst)

# 保存并渲染
dot.render('tiktok_dag.gv', view=True, format='png')