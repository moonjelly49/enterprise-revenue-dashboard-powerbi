// ================= Power Query (Home > Transform data > New Source > Blank Query > Advanced Editor)
// Replace the folder path once, via a parameter named DataPath (Text), e.g. C:\PBI\data\

// ---- fact_sales
let
    Source = Csv.Document(File.Contents(DataPath & "fact_sales.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"OrderID", Int64.Type}, {"OrderDate", type date}, {"CustomerID", Int64.Type},
        {"ProductID", Int64.Type}, {"ChannelID", Int64.Type}, {"RegionID", Int64.Type},
        {"Quantity", Int64.Type}, {"UnitPrice", type number}, {"DiscountPct", type number},
        {"NetRevenue", type number}, {"COGS", type number}}, "en-US"),
    NoNulls = Table.SelectRows(Typed, each [NetRevenue] <> null and [OrderDate] <> null),
    Dedup = Table.Distinct(NoNulls, {"OrderID"})
in
    Dedup

// ---- fact_target
let
    Source = Csv.Document(File.Contents(DataPath & "fact_target.csv"), [Delimiter=",", Encoding=65001]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"TargetMonth", type date}, {"RegionID", Int64.Type},
        {"ChannelID", Int64.Type}, {"RevenueTarget", type number}}, "en-US")
in
    Typed

// ---- dim_customer  (same pattern for dim_region, dim_channel, dim_product)
let
    Source = Csv.Document(File.Contents(DataPath & "dim_customer.csv"), [Delimiter=",", Encoding=65001]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"CustomerID", Int64.Type}, {"CustomerName", type text}, {"Segment", type text},
        {"RegionID", Int64.Type}, {"SignupDate", type date}}, "en-US"),
    Trimmed = Table.TransformColumns(Typed, {{"CustomerName", Text.Trim, type text}})
in
    Trimmed
