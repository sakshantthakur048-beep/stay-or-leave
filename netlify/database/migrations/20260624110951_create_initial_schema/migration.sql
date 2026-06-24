CREATE TABLE "auth_tokens" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"user_id" uuid NOT NULL,
	"token" varchar(255) NOT NULL UNIQUE,
	"token_type" varchar(30) NOT NULL,
	"expires_at" timestamp with time zone NOT NULL,
	"used_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "bookmarks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"user_id" uuid NOT NULL,
	"comparison_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "bookmarks_user_id_comparison_id" UNIQUE("user_id","comparison_id")
);
--> statement-breakpoint
CREATE TABLE "comments" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"review_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"body" varchar(1000) NOT NULL,
	"status" varchar(20) DEFAULT 'published' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "comparisons" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"user_id" uuid,
	"place_a_id" uuid NOT NULL,
	"place_b_id" uuid NOT NULL,
	"recommendation" varchar(10),
	"summary" text,
	"view_count" integer DEFAULT 0 NOT NULL,
	"is_featured" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "contact_messages" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" varchar(100) NOT NULL,
	"email" varchar(255) NOT NULL,
	"subject" varchar(200),
	"message" text NOT NULL,
	"is_read" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "likes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"user_id" uuid NOT NULL,
	"target_type" varchar(20) NOT NULL,
	"target_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "likes_user_id_target_type_target_id" UNIQUE("user_id","target_type","target_id")
);
--> statement-breakpoint
CREATE TABLE "place_metrics" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"place_id" uuid NOT NULL,
	"metric_key" varchar(50) NOT NULL,
	"value" numeric(12,2),
	"unit" varchar(20),
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "place_metrics_place_id_metric_key" UNIQUE("place_id","metric_key")
);
--> statement-breakpoint
CREATE TABLE "places" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" varchar(150) NOT NULL,
	"type" varchar(20) NOT NULL,
	"slug" varchar(170) NOT NULL UNIQUE,
	"country_code" varchar(2),
	"image_url" varchar(500),
	"description" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "reports" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"reporter_id" uuid NOT NULL,
	"target_type" varchar(20) NOT NULL,
	"target_id" uuid NOT NULL,
	"reason" varchar(255) NOT NULL,
	"status" varchar(20) DEFAULT 'pending' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "review_images" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"review_id" uuid NOT NULL,
	"image_url" varchar(500) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "reviews" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"user_id" uuid NOT NULL,
	"place_id" uuid NOT NULL,
	"title" varchar(150) NOT NULL,
	"body" text NOT NULL,
	"rating" smallint NOT NULL,
	"status" varchar(20) DEFAULT 'published' NOT NULL,
	"helpful_count" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" varchar(100) NOT NULL,
	"email" varchar(255) NOT NULL UNIQUE,
	"password_hash" varchar(255) NOT NULL,
	"role" varchar(20) DEFAULT 'user' NOT NULL,
	"profile_picture" varchar(500),
	"is_verified" boolean DEFAULT false NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE INDEX "idx_auth_tokens_token" ON "auth_tokens" ("token");--> statement-breakpoint
CREATE INDEX "idx_auth_tokens_user" ON "auth_tokens" ("user_id");--> statement-breakpoint
CREATE INDEX "idx_bookmarks_user" ON "bookmarks" ("user_id");--> statement-breakpoint
CREATE INDEX "idx_comments_review" ON "comments" ("review_id");--> statement-breakpoint
CREATE INDEX "idx_comments_user" ON "comments" ("user_id");--> statement-breakpoint
CREATE INDEX "idx_comparisons_user" ON "comparisons" ("user_id");--> statement-breakpoint
CREATE INDEX "idx_comparisons_places" ON "comparisons" ("place_a_id","place_b_id");--> statement-breakpoint
CREATE INDEX "idx_comparisons_featured" ON "comparisons" ("is_featured");--> statement-breakpoint
CREATE INDEX "idx_contact_messages_read" ON "contact_messages" ("is_read");--> statement-breakpoint
CREATE INDEX "idx_likes_target" ON "likes" ("target_type","target_id");--> statement-breakpoint
CREATE INDEX "idx_place_metrics_place" ON "place_metrics" ("place_id");--> statement-breakpoint
CREATE INDEX "idx_place_metrics_key" ON "place_metrics" ("metric_key");--> statement-breakpoint
CREATE INDEX "idx_places_type" ON "places" ("type");--> statement-breakpoint
CREATE INDEX "idx_places_name" ON "places" ("name");--> statement-breakpoint
CREATE INDEX "idx_reports_target" ON "reports" ("target_type","target_id");--> statement-breakpoint
CREATE INDEX "idx_reports_status" ON "reports" ("status");--> statement-breakpoint
CREATE INDEX "idx_review_images_review" ON "review_images" ("review_id");--> statement-breakpoint
CREATE INDEX "idx_reviews_place" ON "reviews" ("place_id");--> statement-breakpoint
CREATE INDEX "idx_reviews_user" ON "reviews" ("user_id");--> statement-breakpoint
CREATE INDEX "idx_reviews_status" ON "reviews" ("status");--> statement-breakpoint
CREATE INDEX "idx_reviews_rating" ON "reviews" ("rating");--> statement-breakpoint
CREATE INDEX "idx_users_email" ON "users" ("email");--> statement-breakpoint
ALTER TABLE "auth_tokens" ADD CONSTRAINT "auth_tokens_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "bookmarks" ADD CONSTRAINT "bookmarks_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "bookmarks" ADD CONSTRAINT "bookmarks_comparison_id_comparisons_id_fkey" FOREIGN KEY ("comparison_id") REFERENCES "comparisons"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "comments" ADD CONSTRAINT "comments_review_id_reviews_id_fkey" FOREIGN KEY ("review_id") REFERENCES "reviews"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "comments" ADD CONSTRAINT "comments_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "comparisons" ADD CONSTRAINT "comparisons_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL;--> statement-breakpoint
ALTER TABLE "comparisons" ADD CONSTRAINT "comparisons_place_a_id_places_id_fkey" FOREIGN KEY ("place_a_id") REFERENCES "places"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "comparisons" ADD CONSTRAINT "comparisons_place_b_id_places_id_fkey" FOREIGN KEY ("place_b_id") REFERENCES "places"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "likes" ADD CONSTRAINT "likes_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "place_metrics" ADD CONSTRAINT "place_metrics_place_id_places_id_fkey" FOREIGN KEY ("place_id") REFERENCES "places"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "reports" ADD CONSTRAINT "reports_reporter_id_users_id_fkey" FOREIGN KEY ("reporter_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "review_images" ADD CONSTRAINT "review_images_review_id_reviews_id_fkey" FOREIGN KEY ("review_id") REFERENCES "reviews"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_user_id_users_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_place_id_places_id_fkey" FOREIGN KEY ("place_id") REFERENCES "places"("id") ON DELETE CASCADE;