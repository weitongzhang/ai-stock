import type { Fishpond } from "./types";

export const themePonds: Fishpond[] = [
  {
    id: "ai-optical",
    name: "AI 光通信",
    status: "活跃池",
    kind: "景气鱼塘",
    updated: "2026-06-24",
    thesis: "盈米 AI 产业链研报认为光通信处于 AI 算力链确定性较高的环节：需求强、供给紧、国产替代和技术迭代共同驱动。短线要防拥挤，高质量买点来自回踩承接。",
    events: [
      "海外云厂商资本开支继续传导到 GPU、光模块、交换机和数据中心网络。",
      "800G/1.6T 光模块、硅光、CPO 等技术迭代提升价值量。",
      "光芯片国产替代和高端光器件供给约束，是补涨挖掘重点。"
    ],
    rules: [
      "优先：业绩兑现、订单能见度高、回踩不破均线后重新放量。",
      "谨慎：高位加速后放量长上影，或龙头走弱时后排补涨。",
      "买点不看概念热度本身，必须叠加板块梯队和分时承接。"
    ],
    rows: [
      { category: "光模块龙头", code: "300308", name: "中际旭创", status: "保留", logic: "AI 光模块核心龙头，业绩兑现度高但共识也高。", trigger: "板块强势时缩量回踩后重新放量。", invalidation: "高位放量破位或业绩预期钝化。" },
      { category: "光模块龙头", code: "300502", name: "新易盛", status: "保留", logic: "高速光模块弹性龙头，受益 AI 数据中心需求。", trigger: "龙头梯队同步走强且分时站均价。", invalidation: "板块退潮时高位放量下杀。" },
      { category: "国产替代", code: "002281", name: "光迅科技", status: "观察期", logic: "光器件和光芯片国产替代映射。", trigger: "国产替代事件催化并放量突破。", invalidation: "龙头强而自身无量跟随。" },
      { category: "光通信扩散", code: "300394", name: "天孚通信", status: "观察期", logic: "光器件环节高弹性标的。", trigger: "光模块主线强势时补涨扩散。", invalidation: "冲高回落且板块无梯队。" }
    ]
  },
  {
    id: "ai-pcb-materials",
    name: "AI PCB/CCL 上游材料",
    status: "活跃池",
    kind: "产业鱼塘",
    updated: "2026-06-24",
    thesis: "研报强调 AI 服务器带动 PCB 价值量提升，利润可能向 CCL、高端铜箔、特种玻纤布、高端树脂等上游材料集中。这里适合做核心票映射补涨。",
    events: [
      "AI 服务器高层数、高速板需求提升。",
      "HVLP 铜箔、特种玻纤布、高端树脂和覆铜板供给约束。",
      "PCB 制造龙头强势后，资金可能向上游材料扩散。"
    ],
    rules: [
      "优先：PCB 核心强，材料端放量突破或回踩不破。",
      "铜箔、玻纤、树脂、CCL 是补涨挖掘重点，不只盯 PCB 制造。",
      "若 PCB 龙头集体退潮，上游补涨逻辑同步降级。"
    ],
    rows: [
      { category: "PCB核心", code: "002463", name: "沪电股份", status: "保留", logic: "AI 服务器 PCB 龙头之一，板块风向标。", trigger: "趋势延续且回踩承接。", invalidation: "高位放量破位。" },
      { category: "PCB弹性", code: "300476", name: "胜宏科技", status: "保留", logic: "AI PCB 高弹性核心。", trigger: "放量新高后回踩不破。", invalidation: "连续加速后放量滞涨。" },
      { category: "封装/PCB", code: "002916", name: "深南电路", status: "观察期", logic: "PCB 与封装基板能力兼具。", trigger: "PCB 主线加强时放量修复。", invalidation: "主线强而自身弱。" },
      { category: "CCL", code: "600183", name: "生益科技", status: "保留", logic: "覆铜板中军，承接 PCB 上游利润转移。", trigger: "CCL 涨价或业绩改善预期强化。", invalidation: "跌破趋势且无资金回流。" },
      { category: "玻纤", code: "600176", name: "中国巨石", status: "观察期", logic: "特种玻纤布上游映射，偏低位扩散。", trigger: "玻纤/CCL 方向放量走强。", invalidation: "周期属性拖累且无题材承接。" },
      { category: "高端树脂", code: "605589", name: "圣泉集团", status: "观察期", logic: "高端树脂材料映射 AI PCB 上游。", trigger: "材料端补涨并出现资金承接。", invalidation: "题材扩散失败。" },
      { category: "高端铜箔", code: "301217", name: "铜冠铜箔", status: "观察期", logic: "铜箔高弹性标的，可与 PCB 上游材料共同跟踪。", trigger: "高位分歧后重新转强。", invalidation: "高位连续退潮。" }
    ]
  },
  {
    id: "ai-semi-equipment",
    name: "半导体设备国产替代",
    status: "观察池",
    kind: "景气鱼塘",
    updated: "2026-06-24",
    thesis: "研报认为半导体设备确定性高于纯国产 AI 芯片故事，核心在先进制程、先进封装和国产化率提升。交易上适合等待产业催化和趋势确认。",
    events: [
      "先进制程和先进封装产能紧张。",
      "国产化率提升带来中长期空间。",
      "国产 AI 芯片估值假设偏激进，需要订单和采购验证。"
    ],
    rules: [
      "优先设备、材料、检测等卖铲人环节。",
      "必须看订单、招标、收入兑现，不能只看国产替代口号。",
      "若半导体指数弱，单票只做观察，不贸然加仓。"
    ],
    rows: [
      { category: "平台设备", code: "002371", name: "北方华创", status: "保留", logic: "半导体设备平台型龙头。", trigger: "半导体设备板块放量转强。", invalidation: "趋势破位且板块无承接。" },
      { category: "刻蚀设备", code: "688012", name: "中微公司", status: "保留", logic: "刻蚀设备核心。", trigger: "国产设备主线强化。", invalidation: "高位放量失守关键均线。" },
      { category: "薄膜沉积", code: "688072", name: "拓荆科技", status: "观察期", logic: "薄膜沉积设备弹性标的。", trigger: "设备链扩散时放量突破。", invalidation: "冲高无承接。" },
      { category: "检测设备", code: "688361", name: "中科飞测", status: "观察期", logic: "量测检测设备国产替代。", trigger: "设备链轮动到检测方向。", invalidation: "板块强而自身弱。" }
    ]
  },
  {
    id: "ai-power-layer",
    name: "AI 电力层",
    status: "观察池",
    kind: "扩散鱼塘",
    updated: "2026-06-24",
    thesis: "AI 数据中心扩张最终传导到电力、储能、锂电和电网设备。这个方向赚的是量的扩张，适合做低位扩散和左侧观察。选股重点是储能和出海能力。",
    events: [
      "数据中心用电和配储需求提升。",
      "锂电供需拐点和储能装机增长。",
      "电网设备关注海外订单和出海能力。"
    ],
    rules: [
      "硬件高位拥挤时，资金可能向电力层切换。",
      "优先低位放量、业绩兑现、海外订单清晰的标的。",
      "若只是跟随 AI 概念但没有订单和业绩，维持观察。"
    ],
    rows: [
      { category: "储能中军", code: "300750", name: "宁德时代", status: "保留", logic: "储能和锂电中军，代表电力层容量。", trigger: "储能链强势且指数配合。", invalidation: "权重拖累或锂电链退潮。" },
      { category: "锂电弹性", code: "300014", name: "亿纬锂能", status: "观察期", logic: "锂电与储能弹性。", trigger: "锂电供需拐点被市场交易。", invalidation: "反弹无量或趋势破位。" },
      { category: "电解液", code: "300037", name: "新宙邦", status: "保留", logic: "电解液/电子化学品双重映射，也关联液冷材料。", trigger: "化工材料线和储能线共振。", invalidation: "高位放量滞涨。" },
      { category: "电解液", code: "002709", name: "天赐材料", status: "观察期", logic: "电解液中军，跟踪锂电链修复。", trigger: "锂电材料轮动走强。", invalidation: "板块反弹但自身弱。" }
    ]
  },
  {
    id: "ai-application-left",
    name: "AI 应用左侧观察",
    status: "贫瘠池",
    kind: "观察鱼塘",
    updated: "2026-06-24",
    thesis: "研报对 AI 应用更谨慎：目前还缺杀手级应用和稳定商业化验证。这里不作为核心交易池，只记录事件驱动和可能的左侧变化。",
    events: [
      "大模型从拼参数转向看收入兑现。",
      "AI 应用需要爆款、付费率、利润率或订单验证。",
      "若硬件拥挤退潮，应用端可能出现短期事件轮动。"
    ],
    rules: [
      "没有商业化验证，不升级为核心鱼塘。",
      "只做事件驱动观察，不因泛 AI 标签追高。",
      "出现真实收入、用户增长或爆款产品，再重新评估。"
    ],
    rows: [
      { category: "办公AI", code: "688111", name: "金山办公", status: "观察期", logic: "AI 办公商业化观察样本。", trigger: "AI 订阅/付费数据超预期。", invalidation: "估值高且商业化低于预期。" },
      { category: "语料/出版", code: "601928", name: "凤凰传媒", status: "观察期", logic: "内容和语料资产映射。", trigger: "版权、语料或教育 AI 事件催化。", invalidation: "事件兑现后无量承接。" },
      { category: "应用软件", code: "300188", name: "国投智能", status: "观察期", logic: "AI 应用和数据要素方向弹性观察。", trigger: "应用端板块放量轮动。", invalidation: "纯题材脉冲后回落。" }
    ]
  },
  {
    id: "commercial-space",
    name: "商业航天可回收火箭",
    status: "观察池",
    kind: "事件鱼塘",
    updated: "2026-06-24",
    thesis: "蓝箭、星河动力、天兵科技、深蓝航天等非上市火箭公司是事件源，A 股主要跟踪供应链映射和股权映射。",
    events: [
      "蓝箭航天：朱雀三号、液氧甲烷、可重复使用火箭、科创板 IPO。",
      "星河动力：智神星一号可重复使用火箭首飞/复飞节奏。",
      "深蓝航天：酒泉子公司和火箭制造经营范围。",
      "航宇科技明确回应已配套蓝箭航天、星河动力、天兵科技等商业航天客户。"
    ],
    rules: [
      "供应链证据强于股权传闻，优先跟踪已明确配套客户的标的。",
      "金风科技入股蓝箭线索保留，但未穿透前只放待核实。",
      "火箭事件升温 + A 股标的放量 + 板块有梯队，才从观察池升级。"
    ],
    rows: [
      { category: "核心配套", code: "688239", name: "航宇科技", status: "保留", logic: "已配套蓝箭、星河动力、天兵科技等民营火箭厂商。", trigger: "商业航天事件升温且放量突破。", invalidation: "收入占比低或股价无承接。" },
      { category: "股权线索", code: "002202", name: "金风科技", status: "待核实", logic: "市场线索称金风体系入股蓝箭，持股比例待核实。", trigger: "招股书、年报、工商穿透确认。", invalidation: "无法确认持股或市场不认可。" },
      { category: "投资人映射", code: "600282", name: "南钢股份", status: "观察期", logic: "星际荣耀早期融资曾披露南京钢铁参与认购，比例未披露。", trigger: "星际荣耀可重复使用火箭节点升温。", invalidation: "钢铁主业拖累或无承接。" },
      { category: "国家队中军", code: "600118", name: "中国卫星", status: "保留", logic: "卫星制造与空间基础设施中军。", trigger: "卫星互联网或国家队任务带动。", invalidation: "航天军工退潮。" },
      { category: "结构件", code: "301005", name: "超捷股份", status: "保留", logic: "结构件、紧固件弹性标的。", trigger: "火箭事件前资金提前放量。", invalidation: "事件兑现后回落。" },
      { category: "高端材料", code: "688122", name: "西部超导", status: "保留", logic: "钛合金、高温合金材料中军。", trigger: "航天材料池共振。", invalidation: "材料线退潮。" }
    ]
  },
  {
    id: "rubin-coolant",
    name: "Rubin 液冷/冷却液",
    status: "富矿池",
    kind: "产业鱼塘",
    updated: "2026-06-24",
    thesis: "AI 硬件扩散到液冷和冷却液材料，重点看氟化液、有机氟、电子化学品是否持续放量。",
    events: ["Rubin 和 AI 服务器液冷催化。", "巨化股份、新宙邦作为中军/弹性核心的承接。", "永和股份、三美股份等氟化工扩散观察。"],
    rules: ["巨化和新宙邦同步强，鱼塘质量提升。", "核心股放量跌破关键支撑且扩散断掉，降级。"],
    rows: [
      { category: "中军", code: "600160", name: "巨化股份", status: "保留", logic: "氟化工容量中军。", trigger: "回踩承接或放量突破。", invalidation: "放量跌破关键支撑。" },
      { category: "弹性", code: "300037", name: "新宙邦", status: "保留", logic: "电子化学品/有机氟弹性。", trigger: "站稳关键位并放量。", invalidation: "反抽无量或跌破支撑。" },
      { category: "扩散", code: "605020", name: "永和股份", status: "观察期", logic: "氟化工一体化。", trigger: "核心走强后补涨。", invalidation: "核心转弱且不承接。" },
      { category: "扩散", code: "603379", name: "三美股份", status: "观察期", logic: "制冷剂/氟化工扩散。", trigger: "板块扩散时放量。", invalidation: "冲高回落无承接。" }
    ]
  },
  {
    id: "copper-foil",
    name: "铜箔/铜资源映射",
    status: "观察池",
    kind: "映射鱼塘",
    updated: "2026-06-24",
    thesis: "铜冠铜箔高弹性核心和铜陵有色资源中军之间的长期映射链。当前需要重新确认承接。",
    events: ["铜冠铜箔是否保持高成交辨识度。", "铜陵有色是否修复跌停后的承接。", "铜价和有色板块是否重新走强。"],
    rules: ["铜陵重新站回关键位并放量，才恢复观察强度。", "跌停后无修复，短线补涨逻辑失效。"],
    rows: [
      { category: "核心", code: "301217", name: "铜冠铜箔", status: "观察期", logic: "铜箔/PCB 材料高弹性核心。", trigger: "高位分歧后重新转强。", invalidation: "高位连续退潮。" },
      { category: "映射中军", code: "000630", name: "铜陵有色", status: "降级", logic: "铜资源中军，铜箔资产映射。", trigger: "重新站回关键位并放量。", invalidation: "跌停后无修复或继续破位。" }
    ]
  },
  {
    id: "pcb-equipment",
    name: "PCB设备/大族链",
    status: "观察池",
    kind: "子母映射",
    updated: "2026-06-24",
    thesis: "大族数控高弹性核心与大族激光平台映射，是子母/分拆映射模板链。",
    events: ["大族数控是否保持高位辨识度。", "大族激光是否缩量止跌或放量修复。", "PCB、封测、电子设备方向是否继续扩散。"],
    rules: ["大族数控强，大族激光放量修复，鱼塘升级。", "两者同步放量下跌，鱼塘降级。"],
    rows: [
      { category: "核心", code: "301200", name: "大族数控", status: "保留", logic: "PCB 设备高弹性核心。", trigger: "维持高位强度。", invalidation: "高位退潮。" },
      { category: "映射平台", code: "002008", name: "大族激光", status: "观察期", logic: "母公司/平台映射。", trigger: "缩量回踩后放量修复。", invalidation: "持续放量下跌。" }
    ]
  }
];
