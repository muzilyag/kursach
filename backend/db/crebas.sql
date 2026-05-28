/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Created on:     06.05.2026 10:49:19                          */
/*==============================================================*/

/*==============================================================*/
/* Table: Advertising                                           */
/*==============================================================*/
create table Advertising (
   advertising_id        SERIAL               not null,
   advertising_name     VARCHAR(100)         null,
   advertising_duration TIME                 not null
      constraint CKC_ADVERTISING_DURAT_ADVERTIS check (advertising_duration >= '00:00:00'),
   advertising_owner    VARCHAR(100)         not null,
   advertising_start_date DATE                 not null,
   advertising_finish_date DATE                 not null,
   constraint PK_ADVERTISING primary key (advertising_id)
);

/*==============================================================*/
/* Index: Advertising_PK                                        */
/*==============================================================*/
create unique index Advertising_PK on Advertising (
advertising_id
);

/*==============================================================*/
/* Table: Associate                                             */
/*==============================================================*/
create table Associate (
   content_id           INT4                 not null,
   tag_id               INT4                 not null,
   constraint PK_ASSOCIATE primary key (content_id, tag_id)
);

/*==============================================================*/
/* Index: Associate_PK                                          */
/*==============================================================*/
create unique index Associate_PK on Associate (
content_id,
tag_id
);

/*==============================================================*/
/* Index: Associate_FK                                          */
/*==============================================================*/
create  index Associate_FK on Associate (
tag_id
);

/*==============================================================*/
/* Index: Associate_FK2                                         */
/*==============================================================*/
create  index Associate_FK2 on Associate (
content_id
);

/*==============================================================*/
/* Table: Content                                               */
/*==============================================================*/
create table Content (
   content_id           SERIAL               not null,
   content_duration     TIME                 not null,
   content_publish_date DATE                 null,
   content_name         VARCHAR(100)         not null,
   content_description  TEXT                 null,
   content_type         VARCHAR(50)          not null,
   constraint PK_CONTENT primary key (content_id)
);

/*==============================================================*/
/* Index: Content_PK                                            */
/*==============================================================*/
create unique index Content_PK on Content (
content_id
);

/*==============================================================*/
/* Index: idx_content_name                                      */
/*==============================================================*/
create  index idx_content_name on Content (
content_name
);

/*==============================================================*/
/* Table: Copyright_holder                                      */
/*==============================================================*/
create table Copyright_holder (
   copyright_holder_id  SERIAL               not null,
   copyright_holder_name VARCHAR(100)         not null,
   copyright_holder_phone VARCHAR(15)          not null,
   copyright_holder_email VARCHAR(100)         not null,
   constraint PK_COPYRIGHT_HOLDER primary key (copyright_holder_id)
);

/*==============================================================*/
/* Index: Copyright_holder_PK                                   */
/*==============================================================*/
create unique index Copyright_holder_PK on Copyright_holder (
copyright_holder_id
);

/*==============================================================*/
/* Table: Genre                                                 */
/*==============================================================*/
create table Genre (
   genre_id             SERIAL               not null,
   genre_name           VARCHAR(50)          not null,
   constraint PK_GENRE primary key (genre_id)
);

/*==============================================================*/
/* Index: Genre_PK                                              */
/*==============================================================*/
create unique index Genre_PK on Genre (
genre_id
);

/*==============================================================*/
/* Table: Interest                                              */
/*==============================================================*/
create table Interest (
   user_id              INT4                 not null,
   tag_id               INT4                 not null,
   constraint PK_INTEREST primary key (user_id, tag_id)
);

/*==============================================================*/
/* Index: Interest_PK                                           */
/*==============================================================*/
create unique index Interest_PK on Interest (
user_id,
tag_id
);

/*==============================================================*/
/* Index: Interest_FK                                           */
/*==============================================================*/
create  index Interest_FK on Interest (
tag_id
);

/*==============================================================*/
/* Index: Interest_FK2                                          */
/*==============================================================*/
create  index Interest_FK2 on Interest (
user_id
);

/*==============================================================*/
/* Table: "Is"                                                  */
/*==============================================================*/
create table "Is" (
   genre_id             INT4                 not null,
   content_id           INT4                 not null,
   constraint PK_IS primary key (genre_id, content_id)
);

/*==============================================================*/
/* Index: Is_PK                                                 */
/*==============================================================*/
create unique index Is_PK on "Is" (
genre_id,
content_id
);

/*==============================================================*/
/* Index: Is_FK2                                                */
/*==============================================================*/
create  index Is_FK2 on "Is" (
content_id
);

/*==============================================================*/
/* Index: Is_FK3                                                */
/*==============================================================*/
create  index Is_FK3 on "Is" (
genre_id
);

/*==============================================================*/
/* Table: Own                                                   */
/*==============================================================*/
create table Own (
   content_id           INT4                 not null,
   copyright_holder_id  INT4                 not null,
   constraint PK_OWN primary key (content_id, copyright_holder_id)
);

/*==============================================================*/
/* Index: Own_PK                                                */
/*==============================================================*/
create unique index Own_PK on Own (
content_id,
copyright_holder_id
);

/*==============================================================*/
/* Index: Own_FK                                                */
/*==============================================================*/
create  index Own_FK on Own (
copyright_holder_id
);

/*==============================================================*/
/* Index: Own_FK2                                               */
/*==============================================================*/
create  index Own_FK2 on Own (
content_id
);

/*==============================================================*/
/* Table: Payment                                               */
/*==============================================================*/
create table Payment (
   user_id              INT4                 not null,
   payment_number       INT4                 not null,
   subscribe_type_id    INT4                 null,
   subscribe_start      DATE                 null default CURRENT_DATE,
   payment_sum          FLOAT8               not null,
   payment_date         DATE                 not null,
   payment_method       VARCHAR(100)         not null,
   constraint PK_PAYMENT primary key (user_id, payment_number)
);

/*==============================================================*/
/* Index: Payment_PK                                            */
/*==============================================================*/
create unique index Payment_PK on Payment (
user_id,
payment_number
);

/*==============================================================*/
/* Index: Commit_FK                                             */
/*==============================================================*/
create  index Commit_FK on Payment (
user_id
);

/*==============================================================*/
/* Index: Pay_for_FK                                            */
/*==============================================================*/
create  index Pay_for_FK on Payment (
subscribe_type_id,
user_id,
subscribe_start
);

/*==============================================================*/
/* Table: Shown_with                                            */
/*==============================================================*/
create table Shown_with (
   content_id           INT4                 not null,
   advertising_id        INT4                 not null,
   constraint PK_SHOWN_WITH primary key (content_id, advertising_id)
);

/*==============================================================*/
/* Index: Shown_with_PK                                         */
/*==============================================================*/
create unique index Shown_with_PK on Shown_with (
content_id,
advertising_id
);

/*==============================================================*/
/* Index: Shown_with_FK                                         */
/*==============================================================*/
create  index Shown_with_FK on Shown_with (
advertising_id
);

/*==============================================================*/
/* Index: Shown_with_FK2                                        */
/*==============================================================*/
create  index Shown_with_FK2 on Shown_with (
content_id
);

/*==============================================================*/
/* Table: Subscribe                                             */
/*==============================================================*/
create table Subscribe (
   subscribe_type_id    INT4                 not null,
   user_id              INT4                 not null,
   subscribe_start      DATE                 not null,
   subscribe_finish     DATE                 not null,
   constraint PK_SUBSCRIBE primary key (subscribe_type_id, user_id, subscribe_start)
);

/*==============================================================*/
/* Index: Subscribe_PK                                          */
/*==============================================================*/
create unique index Subscribe_PK on Subscribe (
subscribe_type_id,
user_id,
subscribe_start
);

/*==============================================================*/
/* Index: Has_FK                                                */
/*==============================================================*/
create  index Has_FK on Subscribe (
user_id
);

/*==============================================================*/
/* Index: Is_FK                                                 */
/*==============================================================*/
create  index Is_FK on Subscribe (
subscribe_type_id
);

/*==============================================================*/
/* Table: Subscribe_type                                        */
/*==============================================================*/
create table Subscribe_type (
   subscribe_type_id    SERIAL               not null,
   subscribe_type_discription TEXT                 null,
   subscribe_type_name  VARCHAR(50)          not null,
   subscribe_type_max_type_quality INT2                 not null
      constraint CKC_SUBSCRIBE_TYPE_MA_SUBSCRIB check (subscribe_type_max_type_quality >= 1),
   subscribe_type_cost  FLOAT8               not null
      constraint CKC_SUBSCRIBE_TYPE_CO_SUBSCRIB check (subscribe_type_cost >= 0),
   subscribe_type_duration INT4                 not null
      constraint CKC_SUBSCRIBE_TYPE_DU_SUBSCRIB check (subscribe_type_duration >= 0),
   constraint PK_SUBSCRIBE_TYPE primary key (subscribe_type_id)
);

/*==============================================================*/
/* Index: Subscribe_type_PK                                     */
/*==============================================================*/
create unique index Subscribe_type_PK on Subscribe_type (
subscribe_type_id
);

/*==============================================================*/
/* Table: Suitable_for                                          */
/*==============================================================*/
create table Suitable_for (
   advertising_id        INT4                 not null,
   tag_id               INT4                 not null,
   constraint PK_SUITABLE_FOR primary key (advertising_id, tag_id)
);

/*==============================================================*/
/* Index: Suitable_for_PK                                       */
/*==============================================================*/
create unique index Suitable_for_PK on Suitable_for (
advertising_id,
tag_id
);

/*==============================================================*/
/* Index: Suitable_for_FK                                       */
/*==============================================================*/
create  index Suitable_for_FK on Suitable_for (
tag_id
);

/*==============================================================*/
/* Index: Suitable_for_FK2                                      */
/*==============================================================*/
create  index Suitable_for_FK2 on Suitable_for (
advertising_id
);

/*==============================================================*/
/* Table: Tag                                                   */
/*==============================================================*/
create table Tag (
   tag_id               SERIAL               not null,
   tag_name             VARCHAR(50)          not null,
   constraint PK_TAG primary key (tag_id)
);

/*==============================================================*/
/* Index: Tag_PK                                                */
/*==============================================================*/
create unique index Tag_PK on Tag (
tag_id
);

/*==============================================================*/
/* Table: "User"                                                */
/*==============================================================*/
create table "User" (
   user_id              SERIAL               not null,
   user_name            VARCHAR(100)         not null,
   user_email           VARCHAR(100)         not null,
   user_birth_date      DATE                 not null,
   user_registration_date DATE                 not null default CURRENT_DATE,
   user_password        VARCHAR(255)         not null,
   user_role            VARCHAR(20)          not null,
   constraint PK_USER primary key (user_id),
   constraint UQ_USER_EMAIL unique (user_email)
);

/*==============================================================*/
/* Index: User_PK                                               */
/*==============================================================*/
create unique index User_PK on "User" (
user_id
);

/*==============================================================*/
/* Table: Viewing                                               */
/*==============================================================*/
create table Viewing (
   user_id              INT4                 not null,
   content_id           INT4                 not null,
   viewing_progress     INT4                 not null
      constraint CKC_VIEWING_PROGRESS_VIEWING check (viewing_progress between 0 and 100),
   viewing_start        TIME                 not null default CURRENT_TIME,
   viewing_finish       TIME                 not null,
   constraint PK_VIEWING primary key (user_id, content_id, viewing_progress)
);

/*==============================================================*/
/* Index: Viewing_PK                                            */
/*==============================================================*/
create unique index Viewing_PK on Viewing (
user_id,
content_id,
viewing_progress
);

/*==============================================================*/
/* Index: Show_FK                                               */
/*==============================================================*/
create  index Show_FK on Viewing (
content_id
);

/*==============================================================*/
/* Index: Watch_FK                                              */
/*==============================================================*/
create  index Watch_FK on Viewing (
user_id
);

alter table Associate
   add constraint FK_ASSOCIAT_ASSOCIATE_CONTENT foreign key (content_id)
      references Content (content_id)
      on delete restrict on update restrict;

alter table Associate
   add constraint FK_ASSOCIAT_ASSOCIATE_TAG foreign key (tag_id)
      references Tag (tag_id)
      on delete restrict on update restrict;

alter table Interest
   add constraint FK_INTEREST_INTEREST_TAG foreign key (tag_id)
      references Tag (tag_id)
      on delete restrict on update restrict;

alter table Interest
   add constraint FK_INTEREST_INTEREST_USER foreign key (user_id)
      references "User" (user_id)
      on delete cascade on update restrict;

alter table "Is"
   add constraint FK_IS_IS_CONTENT foreign key (content_id)
      references Content (content_id)
      on delete restrict on update restrict;

alter table "Is"
   add constraint FK_IS_IS_GENRE foreign key (genre_id)
      references Genre (genre_id)
      on delete restrict on update restrict;

alter table Own
   add constraint FK_OWN_OWN_CONTENT foreign key (content_id)
      references Content (content_id)
      on delete restrict on update restrict;

alter table Own
   add constraint FK_OWN_OWN_COPYRIGH foreign key (copyright_holder_id)
      references Copyright_holder (copyright_holder_id)
      on delete restrict on update restrict;

alter table Payment
   add constraint FK_PAYMENT_COMMIT_USER foreign key (user_id)
      references "User" (user_id)
      on delete restrict on update restrict;

alter table Payment
   add constraint FK_PAYMENT_PAY_FOR_SUBSCRIB foreign key (subscribe_type_id, user_id, subscribe_start)
      references Subscribe (subscribe_type_id, user_id, subscribe_start)
      on delete restrict on update restrict;

alter table Shown_with
   add constraint FK_SHOWN_WI_SHOWN_WIT_ADVERTIS foreign key (advertising_id)
      references Advertising (advertising_id)
      on delete restrict on update restrict;

alter table Shown_with
   add constraint FK_SHOWN_WI_SHOWN_WIT_CONTENT foreign key (content_id)
      references Content (content_id)
      on delete restrict on update restrict;

alter table Subscribe
   add constraint FK_SUBSCRIB_HAS_USER foreign key (user_id)
      references "User" (user_id)
      on delete restrict on update restrict;

alter table Subscribe
   add constraint FK_SUBSCRIB_IS_SUBSCRIB foreign key (subscribe_type_id)
      references Subscribe_type (subscribe_type_id)
      on delete restrict on update restrict;

alter table Suitable_for
   add constraint FK_SUITABLE_SUITABLE__ADVERTIS foreign key (advertising_id)
      references Advertising (advertising_id)
      on delete restrict on update restrict;

alter table Suitable_for
   add constraint FK_SUITABLE_SUITABLE__TAG foreign key (tag_id)
      references Tag (tag_id)
      on delete restrict on update restrict;

alter table Viewing
   add constraint FK_VIEWING_SHOW_CONTENT foreign key (content_id)
      references Content (content_id)
      on delete restrict on update restrict;

alter table Viewing
   add constraint FK_VIEWING_WATCH_USER foreign key (user_id)
      references "User" (user_id)
      on delete cascade on update restrict;

